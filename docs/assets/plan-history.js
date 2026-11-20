/* GAX100 personal plan: observed historical passage shares on a fixed reference axis.
 * Times always originate from published result/split data. Reference km are
 * presentation markers, NOT verified course distance or inferred GPS.
 */
(function(global){
'use strict';
const POINTS=[
 {name:'Start',km:0},
 {name:'Magleberg',km:44},
 {name:'Haväng',km:80},
 {name:'Sandhammaren',km:130},
 {name:'Mål',km:160.934}
];
const valid=x=>typeof x==='number'&&Number.isFinite(x);
const median=a=>{
 const xs=a.filter(valid).sort((x,y)=>x-y),n=xs.length;
 return n?(n%2?xs[(n-1)/2]:(xs[n/2-1]+xs[n/2])/2):null;
};
const stationKey=st=>{
 const text=String(st?.name||'').toLocaleLowerCase('sv');
 if(st?.is_finish)return 'Mål';
 for(const key of ['Magleberg','Haväng','Sandhammaren'])
  if(text.includes(key.toLocaleLowerCase('sv')))return key;
 return null;
};
let promise=null;
function load(boot){
 if(promise)return promise;
 promise=(async()=>{
  const response=await fetch('data/historical-checkpoint-km.json');
  if(!response.ok)throw Error('Historisk kilometerproveniens kunde inte läsas');
  const provenance=await response.json();
  if(provenance?.schema!=='gax100-historical-station-distance-provenance-1')
   throw Error('Okänd version av historisk kilometerproveniens');
  const eligible=(boot?.editions||[]).filter(ed=>ed.year>=2014&&ed.year<=2024);
  const results=await Promise.all(eligible.map(async ed=>{
   try{
    const r=await fetch('data/races/'+encodeURIComponent(ed.race_key)+'.json');
    if(!r.ok)throw Error('HTTP '+r.status);
    const race=await r.json();
    if(race.race_key!==ed.race_key||race.demo_only||
      !Array.isArray(race.results)||!Array.isArray(race.splits)||
      !Array.isArray(race.stations))throw Error('Resultatfilens kontrakt är felaktigt');
    return {race,ed};
   }catch(error){return {ed,error:String(error?.message||'Fel vid läsning')};}
  }));
  const editions=results.filter(item=>item.race);
  if(!editions.length)throw Error('Inga historiska kontrollpassager kunde hämtas');
  return {editions,provenance,failed:results.filter(item=>item.error).map(item=>item.ed.edition_label)};
 })().catch(error=>{promise=null;throw error;});
 return promise;
}
function groupSex(row,editionKey,overlays){
 if(row.sex==='F'||row.sex==='M')return row.sex;
 const id=String(row.id);
 const official=(overlays?.official?.editions?.[editionKey]||[]).find(v=>String(v.result_id)===id);
 if(official?.sex==='F'||official?.sex==='M')return official.sex;
 const manual=(overlays?.manual?.editions?.[editionKey]||[]).find(v=>String(v.result_id)===id);
 if(manual?.group_sex==='F'||manual?.group_sex==='M')return manual.group_sex;
 const estimated=(overlays?.estimated?.editions?.[editionKey]||[]).find(v=>String(v.result_id)===id);
 return estimated?.estimated_sex==='F'||estimated?.estimated_sex==='M'?estimated.estimated_sex:null;
}
function sourceQuality(provenance,key){
 const stationSources=provenance?.editions?.[key]?.stations;
 if(!stationSources)return 0.7;
 const modes=POINTS.slice(1,-1).map(p=>stationSources[p.name]?.mode);
 if(modes.some(m=>m==='conflicting_source'))return 0.65;
 if(modes.some(m=>m==='historical_estimate'))return 0.80;
 if(modes.every(m=>m==='year_verified'))return 1;
 return 0.7;
}
function collect(history,overlays){
 const all=[];
 for(const {race,ed} of history.editions){
  const stationByUid=new Map();
  for(const station of race.stations){
   const key=stationKey(station);
   if(key)stationByUid.set(String(station.uid),key);
  }
  const timesByRunner=new Map();
  for(const split of race.splits){
   const station=stationByUid.get(String(split.station_uid));
   if(!station||station==='Mål'||!valid(split.elapsed_seconds)||split.elapsed_seconds<=0)continue;
   const key=String(split.result_id),times=timesByRunner.get(key)||{};
   if(times[station]!==undefined&&times[station]!==split.elapsed_seconds){
    times.invalid=true;
   }else times[station]=split.elapsed_seconds;
   timesByRunner.set(key,times);
  }
  const quality=sourceQuality(history.provenance,ed.race_key);
  for(const row of race.results){
   if(row.status!=='FINISHED'||!valid(row.finish_seconds)||row.finish_seconds<=0)continue;
   const times=timesByRunner.get(String(row.id));
   if(!times||times.invalid)continue;
   const clock=[0,times.Magleberg,times['Haväng'],times.Sandhammaren,row.finish_seconds];
   let prev=0,consistent=true;
   for(const current of clock.slice(1)){
    if(!valid(current))continue;
    if(current<=prev||current>row.finish_seconds){consistent=false;break;}
    prev=current;
   }
   if(!consistent)continue;
   const ratios=[];
   for(let i=0;i<4;i++){
    const from=clock[i],to=clock[i+1];
    ratios.push(valid(from)&&valid(to)&&to>from?
      (to-from)/row.finish_seconds:null);
   }
   if(!ratios.some(x=>valid(x)&&x>0&&x<1))continue;
   all.push({year:ed.year,edition:ed.race_key,quality,seconds:row.finish_seconds,
     sex:groupSex(row,ed.race_key,overlays),className:row.class_name||null,ratios});
  }
 }
 return all;
}
function weight(edition,targetEdition,targetYear,quality){
 const distance=Math.abs(Number(edition.slice(0,4))-targetYear);
 const proximity=1/(1+distance/8);
 const sameEdition=edition===targetEdition?2.5:1;
 // 2024 was a changed course. Its observed clock proportions are informative
 // but not directly equivalent to older course versions.
 const era=targetYear>=2024?
   (Number(edition.slice(0,4))>=2024?1.7:1):
   (Number(edition.slice(0,4))>=2024?0.75:1);
 return quality*proximity*sameEdition*era;
}
function segmentEstimate(rows,index,targetEdition,targetYear){
 const years=new Map();
 for(const sample of rows){
  const ratio=sample.ratios[index];
  if(!valid(ratio)||ratio<=0||ratio>=1)continue;
  const group=years.get(sample.edition)||{ratios:[],quality:sample.quality};
  group.ratios.push(ratio);years.set(sample.edition,group);
 }
 let n=0,total=0,weighted=0;
 for(const [edition,group] of years){
  n+=group.ratios.length;
  const m=median(group.ratios);
  const w=weight(edition,targetEdition,targetYear,group.quality)*
    Math.sqrt(Math.min(25,group.ratios.length));
  total+=w;weighted+=w*m;
 }
 return {ratio:total>0?weighted/total:null,n,years:[...years.keys()].sort()};
}
function matches(r,cohort,target,className){
 if(cohort==='F'||cohort==='M')return r.sex===cohort;
 if(cohort==='near')return Math.abs(r.seconds-target)<=target*.10;
 if(cohort==='class')return r.className===className;
 return true;
}
function build(history,{edition,target,cohort='all',className='',overlays={}}){
 if(!history||!valid(target)||target<=0)throw Error('Ogiltig måltid eller historiskt underlag');
 const samples=collect(history,overlays),targetYear=Number(edition.slice(0,4));
 const filtered=cohort==='all'?samples:samples.filter(row=>matches(row,cohort,target,className));
 const kmTotal=POINTS.at(-1).km,parts=[];
 for(let i=0;i<4;i++){
  let estimate=segmentEstimate(filtered,i,edition,targetYear);
  let expanded=false,fallback=false;
  if(estimate.n<5&&cohort!=='all'){
   estimate=segmentEstimate(samples,i,edition,targetYear);
   expanded=true;
  }
  if(estimate.n<5||!valid(estimate.ratio)||estimate.ratio<=0){
   estimate={ratio:(POINTS[i+1].km-POINTS[i].km)/kmTotal,
     n:0,years:[]};
   fallback=true;
  }
  parts.push({
   index:i,from:POINTS[i],to:POINTS[i+1],km:POINTS[i+1].km-POINTS[i].km,
   share:estimate.ratio,n:estimate.n,years:estimate.years,expanded,fallback,
   method:fallback?'Distansfallback':expanded?'Breddad flerårsmodell':
     estimate.years.length>=2?'Vägd flerårsmodell':'Årsmodell'
  });
 }
 const sum=parts.reduce((n,p)=>n+p.share,0);
 if(!valid(sum)||sum<=0)throw Error('Tidsandelarna kunde inte beräknas');
 let elapsed=0;
 for(const part of parts){
  part.allocation=part.index===parts.length-1?Math.round(target)-elapsed:
    Math.round(target*part.share/sum);
  elapsed+=part.allocation;part.elapsed=elapsed;
 }
 if(parts.some(p=>p.allocation<=0)||elapsed!==Math.round(target))
  throw Error('Loppplanens tidsfördelning är ogiltig');
 return {parts,participants:samples.length,filtered:filtered.length,
  sourceEditions:[...new Set(parts.flatMap(p=>p.years))].sort(),
  failed:history.failed||[],target:Math.round(target)};
}
global.GaxHistoricalPlan={POINTS,load,build,collect};
})(window);

/* Gax100 Splits: public-result classification and ranking integrity.
   This module NEVER guesses sex from a name, and NEVER adds new runners.
   Verified classes are joined ONLY to already privacy-released result IDs.
   Original race JSON and SHA-256 release manifest stay immutable.
*/
(()=>{'use strict';
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const positiveInt=v=>Number.isInteger(v)&&v>0;
const sexOf=r=>r?.sex==='F'||r?.sex==='M'?r.sex:null;
const finish=r=>r?.status==='FINISHED'&&finite(r.finish_seconds)&&r.finish_seconds>0;
function reconcile(race,doc){
 if(!race||!Array.isArray(race.results)||race.demo_only||race.release_state==='PRIVATE_DATA_WITHHELD')
   return{race_key:race?.race_key,applied:0,finish:0};
 const publishedFinishers=race.results.filter(finish);
 const idMap=new Map(publishedFinishers.map(r=>[String(r.id),r]));
 const keyed=doc?.schema==='gax100-confirmed-race-classification-1'?doc.editions?.[race.race_key]:null;
 const source=Array.isArray(keyed)?keyed:[];
 const seen=new Set(),updates=[];
 for(const match of source){
   const key=String(match.result_id);
   if(seen.has(key))throw Error('GAX source classification duplicated one public ID');
   seen.add(key);
   const row=idMap.get(key);
   if(!row||!finite(match.finish_seconds)||row.finish_seconds!==match.finish_seconds)
     throw Error('GAX source classification references unreleased or differing finish time');
   if(match.sex!=='F'&&match.sex!=='M')throw Error('GAX classification is not an explicit M/F race class');
   if(sexOf(row)&&sexOf(row)!==match.sex)
     throw Error('GAX class disagreement with the published race result');
   if(match.overall_rank!=null&&!positiveInt(match.overall_rank))
     throw Error('GAX source overall rank is invalid');
   if(match.sex_class_rank!=null&&!positiveInt(match.sex_class_rank))
     throw Error('GAX source sex class rank is invalid');
   updates.push({row,match});
 }
 // Externally verifiable 2024 safeguard: 18 F + 36 M, all 54 finishers.
 if(race.race_key==='2024-gax100'){
   if(updates.length!==54||updates.filter(x=>x.match.sex==='F').length!==18||
       updates.filter(x=>x.match.sex==='M').length!==36)
     throw Error('GAX 2024 requires the complete verified DUV class list');
 }
 const lookup=new Map(updates.map(({row,match})=>[String(row.id),match]));
 for(const row of race.results){
   row.source_reported_place=positiveInt(row.place)?row.place:null;
   if(!finish(row)){
     row.overall_place=null;row.class_place=null;row.place=null;
     continue;
   }
   const verified=lookup.get(String(row.id));
   if(verified){
     row.sex=verified.sex;
     if(!row.class_name)row.class_name=verified.sex==='F'?'Kvinna':'Man';
     row.sex_provenance='public_official_race_class';
     row.source_confirmed_overall_rank=verified.overall_rank||null;
     row.source_confirmed_class_rank=verified.sex_class_rank||null;
   }
 }
 // Derive real, comparable TOTAL ranking from each finisher's observed
 // official finish_seconds. A source-provided overall rank is kept where
 // it is internally plausible; duplicates at a tied second are permitted.
 const sorted=publishedFinishers.slice().sort((a,b)=>
   a.finish_seconds-b.finish_seconds||String(a.id).localeCompare(String(b.id)));
 for(let i=0;i<sorted.length;i++){
   const row=sorted[i],sameStart=sorted.findIndex(r=>r.finish_seconds===row.finish_seconds);
   const timeRank=sameStart+1,src=row.source_confirmed_overall_rank;
   // Source order can break equal-time ties; reject other disagreements.
   const maxTie=sorted.filter(r=>r.finish_seconds===row.finish_seconds).length;
   const sourcePlausible=positiveInt(src)&&src>=timeRank&&src<timeRank+maxTie;
   const officialRawPlausible=positiveInt(row.source_reported_place)&&
     row.source_reported_place>=timeRank&&row.source_reported_place<timeRank+maxTie;
   row.overall_place=sourcePlausible?src:officialRawPlausible?row.source_reported_place:timeRank;
   row.place=row.overall_place;
   row.place_provenance=sourcePlausible?'duv_confirmed_overall':
     officialRawPlausible?'published_overall':'computed_from_official_finish_time';
 }
 // Class standings MUST come from a documented race class, not a guessed name.
 // For partial-classification editions, never invent official class places for
 // unidentified finishers. DUV class rank has priority where source supplied.
 const coverageComplete=publishedFinishers.every(r=>sexOf(r));
 for(const sex of ['F','M']){
   const members=sorted.filter(r=>sexOf(r)===sex);
   for(let i=0;i<members.length;i++){
     const row=members[i],verified=lookup.get(String(row.id));
     const sourceSexRank=verified?.sex_class_rank;
     const tiedStart=members.findIndex(r=>r.finish_seconds===row.finish_seconds)+1;
     let rank=null,method=null;
     if(positiveInt(sourceSexRank)){rank=sourceSexRank;method='duv_confirmed_class';}
     else if(['2024-gax100','2025-gax100','2026-gax100'].includes(race.race_key)&&
       positiveInt(row.source_reported_place)){rank=row.source_reported_place;method='published_class';}
     else if(coverageComplete){rank=tiedStart;method='computed_complete_class';}
     row.class_place=rank;
     row.class_place_provenance=method;
   }
 }
 return{race_key:race.race_key,applied:updates.length,finish:publishedFinishers.length,
   classified:publishedFinishers.filter(r=>sexOf(r)).length,
   derivedOverall:publishedFinishers.filter(r=>r.place_provenance==='computed_from_official_finish_time').length,
   sourceOverall:publishedFinishers.filter(r=>r.place_provenance!=='computed_from_official_finish_time').length};
}
window.GaxResultIntegrity={reconcile};
})();

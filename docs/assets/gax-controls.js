/* GAX-specific, source-only checkpoint layer on the Sätila Blueprint.
 * No generated GPS positions, no interpolation, no inferred distances.
 * Used only with the same approved race JSON loaded by the site.
 */
(function(){
'use strict';
const $=sel=>document.querySelector(sel);
const h=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const valid=value=>typeof value==='number'&&Number.isFinite(value)&&value>=0;
const time=value=>!valid(value)?'—':(()=>{
 let x=Math.round(value);return Math.floor(x/3600)+':'+String(Math.floor(x/60)%60).padStart(2,'0')+':'+String(x%60).padStart(2,'0');
})();
const median=values=>{
 const s=values.filter(valid).sort((a,b)=>a-b);
 if(!s.length)return null;
 let n=Math.floor(s.length/2);return s.length%2?s[n]:(s[n-1]+s[n])/2;
};
function observed(race,runnerId){
 const out=new Map();
 for(const sp of race.splits||[]){
  if(sp.result_id!==runnerId||!valid(sp.elapsed_seconds)||sp.elapsed_seconds<=0)continue;
  out.set(String(sp.station_uid),sp.elapsed_seconds);
 }
 return out;
}
function stations(race){
 const byStation=new Map();
 for(const st of race.stations||[])byStation.set(String(st.uid),{...st,values:[]});
 for(const split of race.splits||[]){
  const st=byStation.get(String(split.station_uid));
  if(st&&valid(split.elapsed_seconds)&&split.elapsed_seconds>0)st.values.push(split.elapsed_seconds);
 }
 return [...byStation.values()].map(st=>({
   ...st,n:st.values.length,med:st.values.length>=5?median(st.values):null,
   orderMedian:median(st.values)
 })).sort((a,b)=>{
    if(a.is_finish!==b.is_finish)return a.is_finish?1:-1;
    if(a.orderMedian===null)return 1;
    if(b.orderMedian===null)return -1;
    return a.orderMedian-b.orderMedian||String(a.name).localeCompare(String(b.name),'sv');
 });
}
// This display-only provenance never modifies public race JSON or the
// numerical timing axis. Referenced km are not eligible for pace calculations.
let kmReference=null,renderedRace=null,openedRunner=null;
const stationName=st=>{
 const name=String(st.name||'').toLowerCase();
 for(const canonical of ['Magleberg','Haväng','Sandhammaren'])
  if(name.includes(canonical.toLowerCase()))return canonical;
 return null;
};
const sourceEntry=(race,st)=>kmReference?.editions?.[race?.race_key]?.stations?.[stationName(st)]||null;
const kms=v=>Number(v).toLocaleString('sv-SE',{maximumFractionDigits:2});
function displayKm(st,race){
 if(st.is_finish)return '160,9 (nominell 100 miles)';
 const entry=sourceEntry(race,st);
 if(entry?.mode==='conflicting_source'&&entry.alternatives_km?.length){
   const values=[...new Set(entry.alternatives_km)].sort((a,b)=>a-b);
   return values.map(kms).join('–')+' km (källkonflikt)';
 }
 if(valid(st.km))return kms(st.km)+' km (årsresultat)';
 if(entry?.mode==='adjacent_reference'&&valid(entry.reference_km))
   return '≈'+kms(entry.reference_km)+' km (referens, ej årsverifierat)';
 return '— (km ej fastställda)';
}
const kmStatus=(race,st)=>{
 if(st.is_finish)return 'Nominell 100 miles, inte GPX-mätt';
 const entry=sourceEntry(race,st);
 if(entry?.mode==='conflicting_source')return 'Årslistans klassrubriker skiljer; endast tidsanalys';
 if(entry?.mode==='adjacent_reference')return 'Referens från annan upplaga – ej årsverifierat';
 if(entry?.mode==='year_verified'||valid(st.km))return 'Publicerad årskilometer, inte GPX-mätning';
 return 'Årskilometer saknas i verifierad källa';
};
fetch('data/historical-checkpoint-km.json').then(r=>r.ok?r.json():null).then(data=>{
 if(!data||data.schema!=='gax100-historical-station-distance-provenance-1')return;
 kmReference=data;
 if(renderedRace)render(renderedRace);
 if(openedRunner&&renderedRace&&document.querySelector('#profile-dialog')?.open)
  renderProfile(renderedRace,openedRunner);
}).catch(()=>{});

function ensureOverview(){
 let panel=$('#gax-controls-panel');
 if(panel)return panel;
 const section=$('#segments');
 if(!section)return null;
 panel=document.createElement('article');
 panel.className='panel gax-controls-panel';
 panel.id='gax-controls-panel';
 panel.innerHTML='<div class="panel-heading"><h3>Officiella kontrollpassager · Gax100 Splits</h3></div><div id="gax-controls-content" aria-live="polite"></div>';
 const heading=section.querySelector('.section-heading');
 if(heading)heading.insertAdjacentElement('afterend',panel);
 else section.prepend(panel);
 return panel;
}
function render(race){
 renderedRace=race;
 const panel=ensureOverview(),content=$('#gax-controls-content');
 if(!panel||!content)return;
 if(!race||race.release_state==='PRIVATE_DATA_WITHHELD'){
  content.innerHTML='<p class="muted">Kontrollpassagerna finns i den privata, verifierade resultatdatabasen. Individuella kontrolltider visas först när publiceringskontrollerna är godkända.</p>';
  return;
 }
 const demo=Boolean(race.demo_only);
 const title=panel.querySelector('.panel-heading h3');
 if(title)title.textContent=demo?'GAX · simulerade kontrollpassager':'Officiella kontrollpassager · Gax100 Splits';
 const rows=stations(race);
 if(!rows.length){
  content.innerHTML='<p class="muted">Ingen källverifierad kontrollpassage för vald upplaga. Sluttider kan fortfarande analyseras.</p>';
  return;
 }
 content.innerHTML=(demo?'<p class="muted small">Fiktiva passertider vid kontroller från arrangörens 2027-referensmodell, inte historiskt uppmätta kontrollpassager. Median kräver minst fem simulerade tider.</p>':'<p class="muted small">Varje rad motsvarar en faktisk kontroll i vald upplaga. Ordningen följer medianen av registrerade passertider, inte en antagen GPS-position. Median visas endast vid minst fem verkliga tider.</p>')
 +'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>'+(demo?'Modell-km*':'Käll-km*')+'</th><th>'+(demo?'Simulerade tider (n)':'Observerade tider (n)')+'</th><th>Median passertid</th><th>Datastatus</th></tr></thead><tbody>'
 +'<tr class="gax-start-control"><th scope="row">Start · Ystad</th><td>0</td><td>Startens tidsnoll</td><td>0:00</td><td>Beräkningsankare, ingen uppmätt passage</td></tr>'
 +rows.map(st=>'<tr><th scope="row">'+h(st.name)+'</th><td>'+h(displayKm(st,race))+'</td><td>'+st.n+'</td><td>'+time(st.med)+'</td><td>'+(demo?'Simulerad kontrollpassage':(st.n?'Verifierad tid. ':'Ingen tidsobservation. ')+kmStatus(race,st))+'</td></tr>').join('')
 +'</tbody></table></div>'+(demo?'<p class="muted small">* Kilometer och tider är en pedagogisk modell efter aktuella stationsuppgifter; alla individvärden är fiktiva. Segmentfart presenteras inte som verifierad GPX-fart.</p>':'<p class="muted small">* Årsverifierad km, motstridiga källrubriker och referenser från andra år märks separat. Ej årssäkra referenser får aldrig användas för segmentfart. ”Mål” bygger på officiell sluttid.</p>');
}
function renderProfile(race,runner){
 openedRunner=runner;
 const content=$('#profile-content');
 if(!content||!race||!runner||race.release_state==='PRIVATE_DATA_WITHHELD')return;
 const previous=content.querySelector('#gax-runner-checkpoints');if(previous)previous.remove();
 const data=observed(race,runner.id),rows=stations(race).filter(st=>data.has(String(st.uid)));
 if(!rows.length)return;
 const panel=document.createElement('section');
 panel.id='gax-runner-checkpoints';panel.className='gax-checkpoint-profile';
 let last=null;
 const body=rows.map(st=>{
  const elapsed=data.get(String(st.uid));
  const delta=last!==null&&elapsed>last?time(elapsed-last):'—';
  last=elapsed>0?elapsed:last;
  return '<tr><th scope="row">'+h(st.name)+'</th><td>'+time(elapsed)+'</td><td>'+delta+'</td><td>'+h(displayKm(st,race))+'</td></tr>';
 }).join('');
 panel.innerHTML='<h3>'+(race.demo_only?'Simulerade kontrollpassager · GAX':'Officiella kontrollpassager · GAX')+'</h3>'
 +'<p class="muted small">'+(race.demo_only?'Samtliga tider är fiktiva och utgår från en modell av loppets aktuella kontroller. Segmenten beräknas mellan påhittade, men stigande passertider.':'Exakta källtider i medianbaserad visningsordning. ”Sedan föregående” beräknas bara när två faktiska klocktider är stigande; saknade passager fylls inte ut.')+'</p>'
 +'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>Ack. tid</th><th>Sedan föregående observerade</th><th>Km, historisk källa / referens</th></tr></thead><tbody><tr class="gax-start-control"><th scope="row">Start · Ystad</th><td>0:00</td><td>—</td><td>0</td></tr>'+body+'</tbody></table></div>'+(!race.demo_only&&rows.length===1&&rows[0].is_finish?'<p class="gax-timing-note">Denna upplaga har bara officiell målpassage. Tiden Start → Mål är ett verkligt totalresultat; historiska mellankontroller saknas i den publicerade datakällan.</p>':'')+(kmReference?.editions?.[race.race_key]?.stations&&rows.some(st=>!st.is_finish)?'<p class="muted small">Historiska km från resultatlistan eller uttryckligen märkta referenser. Källkonflikter används inte för att beräkna segmentfart.</p>':'');
 content.appendChild(panel);
}
function renderComparison(race,a,b){
 const content=$('#compare-content');
 if(!content||!race||!a||!b||race.release_state==='PRIVATE_DATA_WITHHELD')return;
 const old=content.querySelector('#gax-direct-controls');if(old)old.remove();
 const obsA=observed(race,a.id),obsB=observed(race,b.id);
 const rows=stations(race).filter(st=>obsA.has(String(st.uid))&&obsB.has(String(st.uid)));
 const panel=document.createElement('section');
 panel.id='gax-direct-controls';panel.className='gax-checkpoint-profile';
 panel.innerHTML='<h3>'+(race.demo_only?'Jämför simulerade kontrollpassager':'Gemensamma officiella kontrollpassager')+'</h3>'
 +'<p class="muted small">'+(race.demo_only?'Båda löparna är fiktiva. Tiderna är modellerade och används bara för att granska analysfunktionerna.':'A och B visar källans ackumulerade tid. Skillnaden är B minus A, positivt värde betyder att A passerade tidigare. Endast faktiskt registrerade tider jämförs.')+'</p>'
 +(rows.length?'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>A</th><th>B</th><th>B − A</th></tr></thead><tbody>'
 +rows.map(st=>{
 const x=obsA.get(String(st.uid)),y=obsB.get(String(st.uid)),diff=y-x;
 return '<tr><th scope="row">'+h(st.name)+'</th><td>'+time(x)+'</td><td>'+time(y)+'</td><td>'+(diff>0?'+':diff<0?'−':'')+time(Math.abs(diff))+'</td></tr>';
 }).join('')+'</tbody></table></div>'
 :'<p class="muted">Inga gemensamma, registrerade kontrollpassager utöver sluttiderna.</p>');
 content.appendChild(panel);
}
window.GaxCheckpointView={
 render,renderProfile,renderComparison,
 // Canonical source-timed station sequence and display-only historical km.
 // Neither API transforms result rows or creates geographical positions.
 sourceStations:race=>stations(race).filter(st=>st.n>0),
 formatKm:(race,station)=>displayKm(station,race),
 _test:{median,observed,stations}
};
})();
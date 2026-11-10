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
function displayKm(st){
 // Finish uses the nominal definition of 100 miles, not an observed source kilometre.
 if(st.is_finish)return '—';
 return valid(st.km)?Number(st.km).toLocaleString('sv-SE',{maximumFractionDigits:2})+'*':'—';
}
function ensureOverview(){
 let panel=$('#gax-controls-panel');
 if(panel)return panel;
 const section=$('#segments');
 if(!section)return null;
 panel=document.createElement('article');
 panel.className='panel gax-controls-panel';
 panel.id='gax-controls-panel';
 panel.innerHTML='<div class="panel-heading"><h3>GAX · officiella kontrollpassager</h3></div><div id="gax-controls-content" aria-live="polite"></div>';
 const heading=section.querySelector('.section-heading');
 if(heading)heading.insertAdjacentElement('afterend',panel);
 else section.prepend(panel);
 return panel;
}
function render(race){
 const panel=ensureOverview(),content=$('#gax-controls-content');
 if(!panel||!content)return;
 if(!race||race.release_state==='PRIVATE_DATA_WITHHELD'){
  content.innerHTML='<p class="muted">Kontrollpassagerna finns i den privata, verifierade resultatdatabasen. Individuella kontrolltider visas först när publiceringskontrollerna är godkända.</p>';
  return;
 }
 const rows=stations(race);
 if(!rows.length){
  content.innerHTML='<p class="muted">Ingen källverifierad kontrollpassage för vald upplaga. Sluttider kan fortfarande analyseras.</p>';
  return;
 }
 content.innerHTML='<p class="muted small">Varje rad motsvarar en faktisk kontroll i vald upplaga. Ordningen följer medianen av registrerade passertider, inte en antagen GPS-position. Median visas endast vid minst fem verkliga tider.</p>'
 +'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>Käll-km*</th><th>Observerade tider (n)</th><th>Median passertid</th><th>Datastatus</th></tr></thead><tbody>'
 +rows.map(st=>'<tr><th scope="row">'+h(st.name)+'</th><td>'+h(displayKm(st))+'</td><td>'+st.n+'</td><td>'+time(st.med)+'</td><td>'+(st.distance_conflict?'Km-konflikt – tidsanalys enbart':st.n?'Verifierad tidsobservation':'Ingen tidsobservation')+'</td></tr>').join('')
 +'</tbody></table></div><p class="muted small">* Källans kilometerangivelser är inte verifierad årsspecifik GPS-distans. Inga km/h- eller min/km-värden beräknas här. ”Mål” bygger på officiell sluttid och visas skilt från mellankontrollerna.</p>';
}
function renderProfile(race,runner){
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
  return '<tr><th scope="row">'+h(st.name)+'</th><td>'+time(elapsed)+'</td><td>'+delta+'</td><td>'+h(displayKm(st))+'</td></tr>';
 }).join('');
 panel.innerHTML='<h3>Officiella kontrollpassager · GAX</h3>'
 +'<p class="muted small">Exakta källtider i medianbaserad visningsordning. ”Sedan föregående” beräknas bara när två faktiska klocktider är stigande; saknade passager fylls inte ut.</p>'
 +'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>Ack. tid</th><th>Sedan föregående observerade</th><th>Käll-km*</th></tr></thead><tbody>'+body+'</tbody></table></div>';
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
 panel.innerHTML='<h3>Gemensamma officiella kontrollpassager</h3>'
 +'<p class="muted small">A och B visar källans ackumulerade tid. Skillnaden är B minus A, positivt värde betyder att A passerade tidigare. Endast faktiskt registrerade tider jämförs.</p>'
 +(rows.length?'<div class="table-scroll"><table class="gax-check-table"><thead><tr><th>Kontroll</th><th>A</th><th>B</th><th>B − A</th></tr></thead><tbody>'
 +rows.map(st=>{
 const x=obsA.get(String(st.uid)),y=obsB.get(String(st.uid)),diff=y-x;
 return '<tr><th scope="row">'+h(st.name)+'</th><td>'+time(x)+'</td><td>'+time(y)+'</td><td>'+(diff>0?'+':diff<0?'−':'')+time(Math.abs(diff))+'</td></tr>';
 }).join('')+'</tbody></table></div>'
 :'<p class="muted">Inga gemensamma, registrerade kontrollpassager utöver sluttiderna.</p>');
 content.appendChild(panel);
}
window.GaxCheckpointView={render,renderProfile,renderComparison,
 _test:{median,observed,stations}};
})();
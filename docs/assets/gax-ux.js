/* GAX100 – compact analysis navigation, method help and accessible stage dialog.
 * UI only. Does not read or publish personal runner/source data.
 */
(()=>{
'use strict';
const $=(q,root=document)=>root.querySelector(q);
const $$=(q,root=document)=>Array.from(root.querySelectorAll(q));
const HELP={
 'race-context':'Välj loppår eller 2021-A/B. Fältet under årsväljaren berättar om innehållet är en fiktiv design-demo eller en källa som har passerat publiceringskontrollerna. Kartor och kontrollpunkter kan skilja sig mellan upplagorna.',
 method:'Metodavsnittet skiljer på officiella årsantal, fiktiva analysvärden och lokalt inlästa GPX-filer. I den här granskningssidan är varje enskild löpares namn, kön, tider och kontrollpassager påhittade.',
 overview:'Översikten visar fördelningen av starter, fullföljare och sluttider. Diagram och tabeller följer valda filter. I designversionen är enskilda resultat och kön simulerade; årens antal hämtas från arrangörskällor.',
 dynamics:'Här hittar du placeringar, starka avslutningar och avvikande prestationer. Jämför löpare inom samma upplaga. I designversionen bygger analyserna på fiktiva passertider och placeringar.',
 segments:'Hela loppet visar fördelningar för varje delsträcka. Växla till Min loppplan och ange din önskade sluttid för att få en fördelning av tiden per kontroll. Standardvärdet är fältets median. I demoversionen används simulerade tider; det är ingen prognos.',
 course:'Banpanelen visar en GPX endast när en årsbunden fil har valts lokalt. Bangeometri är inte samma sak som en löpares uppmätta GPS-position. Höjdskillnader inom en segmentanalys kräver verkliga georefererade kontroller.',
 history:'Historik visar resultatantal och status för varje upplaga. 2021-A och 2021-B är separata lopp. Jämförelser av fysisk prestation mellan år kräver dokumenterat jämförbar bansträckning.',
 results:'Sök, sortera och öppna en löparprofil. Förhandsversionen innehåller enbart påhittade svenska namn, klubbar, tider och kön. Årens officiella antal ligger kvar som referens.',
 'map-duel-builder':'Välj två till fem löpare och jämför deras passertider. För Kartduell måste du öppna en egen GPX-fil för vald upplaga. Kartmarkörerna rör sig genom interpolation mellan modellkontrollerna – de är inte löparnas uppmätta GPS-spår.',
 'runner-tools':'Sök efter en löpare i vald upplaga. Tryck på namnet för att se profil, segment och jämförelse. Alla individer är fiktiva i den publika designversionen.',
 'gax-guide-dialog':'Loppets fyra naturavsnitt och arrangörens vätskestationer visas som en översikt. Reptiderna gäller den aktuella publicerade tävlingsinformationen och ska inte tolkas som exakt samma historiska bana för varje upplaga.'
};
const CARD_HELP={
 'Start till mål':'Andelen som fullföljt visas separat för kvinnor och män. Under staplarna finns en komprimerad klassfördelning inom aktuellt urval. DNS räknas inte som startande.',
 'Prestationer som sticker ut':'Fem olika sätt att hitta uppseendeväckande lopp. Starkaste avslutningen jämför tempot före och efter ungefär två tredjedelar av banan, normaliserat mot andra löpare av samma kön. I demon är tiderna simulerade.',
 'Banans dimensioner':'Arrangörens tävlingsdistans, antalet modellkontroller, sluttidsmedian och DNF-andel. En verklig GPX-distans anges separat enbart om användaren har läst in en årsrutt. Ingen tom dubblettdistans visas.',
 'Andel kvinnor och män över tid':'Andelen kvinnor och män per upplaga. I designversionen kommer detta från syntetiskt kön per demolöpare; endast 2026 års fördelning har kalibrerats mot publicerade totalsiffror. Kurvorna visar inte verklig historisk demografi.',
 'Vad går att jämföra?':'Tabellen redovisar tidigare kartinventering separat från de offentliga resultatfilerna. En identifierad kandidatrutt är inte automatiskt en officiell bana; ingen GPX återpubliceras utan tillstånd.',
 'Fördela din måltid över delsträckorna':'Skriv en önskad sluttid. Modellen fördelar den utifrån medianandel av sluttiden på respektive delsträcka. Hela loppets median visas som startvärde. Alla demoresultat är simulerade.',
 'Fältets segmenttider, segment för segment':'Varje segment kräver giltiga, stigande tidsankare. Median och spridning gäller aktuellt köns- och statusurval; tomma eller brutna passager blir inte noll.',
 'Spurten mot mål':'Jämför en löpares sista registrerade segment med andra fullföljare. I demoversionen är både loppet och kontrolltiderna påhittade.',
 'GAX · simulerade kontrollpassager':'Samtliga kontrolltider i den publika demon är fiktiva. Modellkilometer används för att pröva graferna men ska inte tolkas som verklig tidtagning.'
};
const human=(node)=>String(node?.textContent||'').trim().replace(/\s+/g,' ');
function showInformation(title,message){
 const dlg=$('#help-dialog');
 if(!dlg){return}
 $('#help-title').textContent=title;
 $('#help-content').textContent=message;
 if(!dlg.open)dlg.showModal();
}
function addInfo(host,titleKey,message){
 if(!host||$('.info',host)||$('.gax-added-info',host))return;
 const heading=$('h2,h3',host);
 if(!heading)return;
 const button=document.createElement('button');
 button.type='button';
 button.className='info gax-added-info';
 button.textContent='i';
 button.setAttribute('aria-label','Förklaring: '+titleKey);
 button.dataset.gaxHelpTitle=titleKey;
 button.dataset.gaxHelpText=message;
 host.appendChild(button);
}
function decorate(){
 $$('section.section').forEach(section=>{
   if(section.closest('#gax-guide-dialog'))return;
   const heading=$(':scope > .section-heading',section);
   if(heading)addInfo(heading,human($('h2',heading)),HELP[section.id]||'Avsnittet visar resultat eller metod för aktuell upplaga. Välj år och granska underlaget genom metodinformationen vid analyskorten.');
 });
 const context=$('#race-context .context-main');
 if(context)addInfo(context,'Loppår och datatyp',HELP['race-context']);
 const method=$('#method');
 if(method&&!$('.gax-added-info',method)){
   const title=$('h2',method);
   if(title){
     const btn=document.createElement('button');
     btn.className='info gax-added-info';
     btn.type='button';
     btn.textContent='i';
     btn.setAttribute('aria-label','Förklaring: Metod och datakällor');
     btn.dataset.gaxHelpTitle='Så ska metodinformationen tolkas';
     btn.dataset.gaxHelpText=HELP.method;
     title.after(btn);
   }
 }
  $('article.panel').forEach(card=>{
   const heading=$(':scope > .panel-heading',card);
   if(!heading)return;
   const title=human($('h3',heading));
   if(!title)return;
   addInfo(heading,title,CARD_HELP[title]||'Analysen gäller det aktuella loppåret och resultatfiltreringen. Minst fem jämförbara observationer krävs för en stabil gruppmedian. I designversionen är alla individuella värden fiktiva.');
 });
}
function planMode(mode){
 const analysis=$('#gax-segment-analytics'),personal=$('#gax-personal-plan-panel');
 if(!analysis||!personal)return;
 const mine=mode==='personal';
 analysis.hidden=mine;personal.hidden=!mine;
 const extras=$('#extra-segments');if(extras)extras.hidden=mine;
 $$('[data-gax-mode]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.gaxMode===mode)));
 $('#segments')?.setAttribute('data-plan-mode',mode);
 if(mine){
   const field=$('#target-time'),src=$('#plan-summary');
   if(field&&!field.value&&src)src.textContent='Mediantiden i fältet används som standard. Ange valfri sluttid för att anpassa planen.';
   field?.focus({preventScroll:true});
 }
}
function init(){
 const dlg=$('#gax-guide-dialog');
 if(dlg){
   dlg.addEventListener('click',event=>{if(event.target===dlg)dlg.close()});
 }
 document.addEventListener('click',event=>{
   const open=event.target.closest('[data-gax-open-guide]');
   if(open){event.preventDefault();if(dlg&&!dlg.open)dlg.showModal();return}
   const close=event.target.closest('.gax-guide-close');
   if(close){dlg?.close();return}
   const mode=event.target.closest('[data-gax-mode]');
   if(mode){planMode(mode.dataset.gaxMode);return}
   const button=event.target.closest('.gax-added-info');
   if(button){event.stopImmediatePropagation();showInformation(button.dataset.gaxHelpTitle,button.dataset.gaxHelpText)}
 },true);
 const observer=new MutationObserver(mutations=>{
   if(mutations.some(m=>Array.from(m.addedNodes).some(n=>n.nodeType===1&&
       (n.matches?.('.extra-grid,article.panel')||n.querySelector?.('.extra-grid,article.panel'))))){
     decorate();
     if($('#segments')?.dataset.planMode==='personal')$('#extra-segments')?.setAttribute('hidden','');
   }
 });
 for(const id of ['overview','dynamics','segments','course','history','results']){
   const root=$('#'+id);if(root)observer.observe(root,{childList:true,subtree:false});
 }
 decorate();planMode('analysis');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();

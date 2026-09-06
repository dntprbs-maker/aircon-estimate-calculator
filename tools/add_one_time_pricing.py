from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
# Add one-time mode styles
needle='/* 거래처별 가격표 관리 - M1.3.1 확장 */'
styles='''/* 이번만 단가표 */\n.one-time-unit{display:inline-flex;align-items:center;gap:5px}.one-time-unit input{width:112px;height:36px;border:1.5px solid #2563eb;border-radius:9px;padding:0 8px;text-align:right;font-size:14px;font-weight:800;background:#eff6ff}.one-time-note{margin-top:7px;padding:8px 10px;border-radius:10px;background:#fff7ed;color:#9a3412;font-size:12px;font-weight:800}@media(max-width:560px){.one-time-unit input{width:104px}}\n\n'''
if styles not in s:s=s.replace(needle,styles+needle)
# Add special option in selector refresh
old="e.innerHTML='<option value=\"base\">기본 가격표</option>'+priceProfiles.map(x=>`<option value=\"${x.id}\">${esc(x.name)}</option>`).join('');"
new="e.innerHTML='<option value=\"base\">기본 가격표</option>'+priceProfiles.map(x=>`<option value=\"${x.id}\">${esc(x.name)}</option>`).join('')+'<option value=\"oneTime\">이번만 단가표</option>';"
s=s.replace(old,new)
# Keep oneTime valid in selector
s=s.replace("if(activeProfileId!=='base'&&!priceProfiles.some(x=>x.id===activeProfileId))activeProfileId='base';","if(activeProfileId!=='base'&&activeProfileId!=='oneTime'&&!priceProfiles.some(x=>x.id===activeProfileId))activeProfileId='base';")
# Replace selector handler and active unit logic
s=s.replace("function selectPriceProfile(){activeProfileId=document.getElementById('priceProfileSelect').value;calculate()}","let oneTimeSourceId='base',oneTimeUnits={};\nfunction selectPriceProfile(){const next=document.getElementById('priceProfileSelect').value;if(next==='oneTime'){if(activeProfileId!=='oneTime')oneTimeSourceId=activeProfileId;oneTimeUnits={};}activeProfileId=next;calculate()}")
s=s.replace("function getActiveUnit(p,t,k){if(activeProfileId==='base')return p[season][t][k];const x=priceProfiles.find(x=>x.id===activeProfileId);return x?normalizeProfileMatrix(x)[p.id][season][t][k]:p[season][t][k]}","function getProfileUnit(profileId,p,t,k){if(profileId==='base'||profileId==='oneTime')return p[season][t][k];const x=priceProfiles.find(x=>x.id===profileId);return x?normalizeProfileMatrix(x)[p.id][season][t][k]:p[season][t][k]}\nfunction oneTimeKey(p,t,k){return `${p.id}|${season}|${t}|${k}`}\nfunction getActiveUnit(p,t,k){if(activeProfileId!=='oneTime')return getProfileUnit(activeProfileId,p,t,k);const key=oneTimeKey(p,t,k);return Object.prototype.hasOwnProperty.call(oneTimeUnits,key)?oneTimeUnits[key]:getProfileUnit(oneTimeSourceId,p,t,k)}\nfunction setOneTimeUnit(id,value){if(activeProfileId!=='oneTime')return;const p=products.find(x=>x.id===id);if(!p)return;const total=products.reduce((sum,x)=>sum+(parseInt(qtyInputs[x.id]?.value)||0),0),t=getTier(total),k=priceType==='service'?0:1,key=oneTimeKey(p,t,k),n=parseInt(String(value).replace(/[^0-9]/g,''),10);if(Number.isFinite(n)&&n>=0)oneTimeUnits[key]=n;calculate()}")
# Add hint under price card
oldhint='<div class="hint">기본 가격표 전체를 복사해 거래처별 가격표를 만들 수 있습니다. 원본 가격표는 변경되지 않습니다.</div></section>'
newhint='<div class="hint">기본 가격표 전체를 복사해 거래처별 가격표를 만들 수 있습니다. 원본 가격표는 변경되지 않습니다.</div><div id="oneTimeNotice" class="one-time-note" style="display:none">이번 견적에만 적용됩니다. 저장된 가격표 원본은 변경되지 않습니다.</div></section>'
s=s.replace(oldhint,newhint)
# Replace unit display line in calculate with editable input only in oneTime
oldline="document.getElementById(`unit-${p.id}`).textContent = `단가 ${fmt(unit)}`;"
newline="const unitEl=document.getElementById(`unit-${p.id}`);if(activeProfileId==='oneTime'){unitEl.innerHTML=`<span class=\"one-time-unit\"><span>단가</span><input type=\"text\" inputmode=\"numeric\" aria-label=\"${esc(p.name)} 이번만 단가\" value=\"${new Intl.NumberFormat('ko-KR').format(unit)}\" data-id=\"${p.id}\"></span>`;const inp=unitEl.querySelector('input');inp.addEventListener('change',()=>setOneTimeUnit(p.id,inp.value));inp.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();inp.blur()}})}else{unitEl.textContent=`단가 ${fmt(unit)}`}"
s=s.replace(oldline,newline)
# Show notice and mark summary
oldcalc="function calculate(){\n  updatePriceSettingSummary();"
newcalc="function calculate(){\n  updatePriceSettingSummary();\n  const oneTimeNotice=document.getElementById('oneTimeNotice');if(oneTimeNotice)oneTimeNotice.style.display=activeProfileId==='oneTime'?'block':'none';"
s=s.replace(oldcalc,newcalc)
# Reset one-time edits on quote reset
s=s.replace("document.getElementById('memo').value='';\n  calculate();","document.getElementById('memo').value='';\n  oneTimeUnits={};\n  calculate();")
p.write_text(s,encoding='utf-8')
print('patched one-time pricing mode')

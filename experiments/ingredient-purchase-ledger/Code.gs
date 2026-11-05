/** 식자재 매입 장부 — Google Apps Script backend.
 * Owner-only web-app, minimum drive.file scope. No DriveApp/SpreadsheetApp.
 * Release: proof-of-concept; Google account/OCR integration not yet live-tested.
 */
const PROP = PropertiesService.getScriptProperties();
const DOC_HEADERS = ['id','date','supplier','type','supply','tax','total','payment','memo','imageId','imageName','relatedId','createdAt','updatedAt','status'];
const ITEM_HEADERS = ['id','docId','name','spec','unit','quantity','unitPrice','amount','active','updatedAt'];
const MAX_IMAGE_BYTES = 8 * 1024 * 1024;

function doGet() {
  return HtmlService.createTemplateFromFile('Index').evaluate()
    .setTitle('식자재 매입 장부')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}
function include(name) {
  if (['Style','Core','Client'].indexOf(name) === -1) throw new Error('Invalid include');
  return HtmlService.createHtmlOutputFromFile(name).getContent();
}
function fetchApi(url,options) {
  options = options || {};
  const headers = Object.assign({}, options.headers || {}, {Authorization:'Bearer ' + ScriptApp.getOAuthToken()});
  const request = Object.assign({muteHttpExceptions:true},options); request.headers=headers;
  const response = UrlFetchApp.fetch(url, request);
  const status = response.getResponseCode();
  if (status < 200 || status >= 300) {
    // Do not disclose OAuth tokens or sensitive document contents in errors.
    const msg = response.getContentText().slice(0,500).replace(/[\r\n\t]/g,' ');
    throw new Error('Google API 오류 (' + status + '): ' + msg);
  }
  return response;
}
function jsonApi(url,method,object) {
  const opt = {method:method||'get'};
  if (object !== undefined) {
    opt.contentType='application/json; charset=UTF-8';
    opt.payload=JSON.stringify(object);
  }
  const r=fetchApi(url,opt);
  return r.getContentText()?JSON.parse(r.getContentText()):{};
}
function createDriveFolder(name,parentId) {
  return jsonApi('https://www.googleapis.com/drive/v3/files?fields=id,name','post',{
    name:name,mimeType:'application/vnd.google-apps.folder',...(parentId?{parents:[parentId]}:{})
  }).id;
}
function createSpreadsheet(parentId) {
  const file=jsonApi('https://www.googleapis.com/drive/v3/files?fields=id,name','post',{
    name:'식자재 매입 장부 - 데이터',mimeType:'application/vnd.google-apps.spreadsheet',parents:[parentId]
  });
  const id=file.id;
  const meta=jsonApi('https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(id)+'?fields=sheets.properties');
  if (!meta.sheets || !meta.sheets.length) throw new Error('Sheet 생성 결과가 불완전합니다. 파일을 확인해주세요.');
  jsonApi('https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(id)+':batchUpdate','post',{
    requests:[
      {updateSheetProperties:{properties:{sheetId:meta.sheets[0].properties.sheetId,title:'Documents'},fields:'title'}},
      {addSheet:{properties:{title:'Items'}}}
    ]
  });
  sheetsBatch(id,[{range:'Documents!A1:O1',values:[DOC_HEADERS]},{range:'Items!A1:J1',values:[ITEM_HEADERS]}]);
  return id;
}
function sheetsBatch(id,data) {
  return jsonApi('https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(id)+'/values:batchUpdate','post',{
    valueInputOption:'RAW',data:data
  });
}
function getStore() {
  const id=PROP.getProperty('SPREADSHEET_ID'),folder=PROP.getProperty('IMAGE_FOLDER_ID');
  if (!id || !folder) throw new Error('저장소 초기화가 필요합니다. [설정]에서 먼저 초기화하세요.');
  return {id:id,folder:folder};
}
function apiStatus() {
  const id=PROP.getProperty('SPREADSHEET_ID');
  return {ready:!!id,spreadsheetUrl:id?'https://docs.google.com/spreadsheets/d/'+id+'/edit':'',folderUrl:PROP.getProperty('IMAGE_FOLDER_ID')?'https://drive.google.com/drive/u/0/folders/'+PROP.getProperty('IMAGE_FOLDER_ID'):'',backups:JSON.parse(PROP.getProperty('BACKUPS')||'[]')};
}
function apiSetup() {
  const lock=LockService.getScriptLock(); lock.waitLock(30000);
  try {
    if (PROP.getProperty('SPREADSHEET_ID')) return apiStatus();
    let parent=PROP.getProperty('ROOT_FOLDER_ID');
    if (!parent) {parent=createDriveFolder('식자재 매입 장부');PROP.setProperty('ROOT_FOLDER_ID',parent);}
    let images=PROP.getProperty('IMAGE_FOLDER_ID');
    if (!images) {images=createDriveFolder('영수증 원본',parent);PROP.setProperty('IMAGE_FOLDER_ID',images);}
    const id=createSpreadsheet(parent);PROP.setProperty('SPREADSHEET_ID',id);
    return apiStatus();
  } finally {lock.releaseLock();}
}
function sheetValues(id,name,endCol) {
  const range=encodeURIComponent(name+'!A:'+endCol);
  const data=jsonApi('https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(id)+'/values/'+range+'?valueRenderOption=UNFORMATTED_VALUE');
  return data.values || [];
}
function readAll() {
  const store=getStore(),drows=sheetValues(store.id,'Documents','O'),irows=sheetValues(store.id,'Items','J');
  const documents=[];
  for(let i=1;i<drows.length;i++){
    const r=drows[i];if(!r[0])continue;
    const d={id:String(r[0]),date:String(r[1]||''),supplier:String(r[2]||''),type:String(r[3]||'미확인'),
      supply:fromCell(r[4]),tax:fromCell(r[5]),total:fromCell(r[6]),payment:String(r[7]||'미확인'),memo:String(r[8]||''),
      imageId:String(r[9]||''),imageName:String(r[10]||''),relatedId:String(r[11]||''),createdAt:String(r[12]||''),updatedAt:String(r[13]||''),status:String(r[14]||'정상'),items:[],_row:i+1};
    documents.push(d);
  }
  const byId={};documents.forEach(d=>byId[d.id]=d);
  for(let i=1;i<irows.length;i++){
    const r=irows[i],doc=byId[String(r[1]||'')];
    if(!doc || !r[0] || String(r[8]||'').toUpperCase()==='FALSE')continue;
    doc.items.push({id:String(r[0]),name:String(r[2]||''),spec:String(r[3]||''),unit:String(r[4]||''),quantity:fromCell(r[5]),unitPrice:fromCell(r[6]),amount:fromCell(r[7])});
  }
  return {docs:documents,docRows:drows,itemRows:irows,store:store};
}
function fromCell(x) {if(x===undefined||x===null||x==='')return null;const n=Number(String(x).replace(/,/g,''));return Number.isFinite(n)?n:null;}
function toCell(x) {return x===undefined||x===null?'':x;}
function cleanText(s,max) {return String(s===undefined||s===null?'':s).replace(/[\u0000-\u001F]/g,' ').slice(0,max);}
function checkedNumber(x) {if(x==null||String(x).trim()==='')return '';const n=Number(String(x).replace(/,/g,''));if(!Number.isFinite(n) || Math.abs(n)>100000000000)throw new Error('금액/수량이 올바르지 않습니다.');return n;}
function b64bytes(image) {
  if(!image || !/^image\/(jpeg|png|webp|gif)$/.test(image.mime||'')) throw new Error('JPG, PNG, WEBP, GIF 이미지만 지원합니다.');
  if(typeof image.data!=='string'||image.data.length>MAX_IMAGE_BYTES*1.38+100)throw new Error('사진은 8MB 이하로 첨부해주세요.');
  const bytes=Utilities.base64Decode(image.data.replace(/^data:[^,]*,/,''));
  if(!bytes.length || bytes.length>MAX_IMAGE_BYTES)throw new Error('사진 크기가 허용 범위를 벗어났습니다.');
  return bytes;
}
function multipartUpload(meta,bytes,mime,ocr) {
  const boundary='ledger_'+Utilities.getUuid().replace(/-/g,'');
  const p1='--'+boundary+'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+JSON.stringify(meta)+'\r\n'+
    '--'+boundary+'\r\nContent-Type: '+mime+'\r\n\r\n';
  const end='\r\n--'+boundary+'--\r\n';
  const payload=Utilities.newBlob(p1).getBytes().concat(bytes,Utilities.newBlob(end).getBytes());
  const url='https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,mimeType'+(ocr?'&ocrLanguage=ko':'');
  return JSON.parse(fetchApi(url,{method:'post',contentType:'multipart/related; boundary='+boundary,payload:payload}).getContentText());
}
function apiExtract(image) {
  const bytes=b64bytes(image),store=getStore();
  // OCR temporarily creates a Google Doc and exports its text. The uploaded original
  // is NOT saved until the user reviews and chooses Save.
  let tmp='';
  try {
    const created=multipartUpload({name:'OCR 임시 '+new Date().toISOString(),mimeType:'application/vnd.google-apps.document',parents:[PROP.getProperty('ROOT_FOLDER_ID')]},bytes,image.mime,true);
    tmp=created.id;
    const r=fetchApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(tmp)+'/export?mimeType=text%2Fplain');
    return {text:r.getContentText('UTF-8'),method:'Google Drive OCR',notice:'품목 행 및 단가는 원본과 직접 대조하세요.'};
  } finally {
    if(tmp){try {fetchApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(tmp),{method:'delete'});}catch(e){console.warn('OCR temporary file cleanup failed',String(e).slice(0,150));}}
  }
}
function apiList(){const data=readAll();return {docs:data.docs.filter(d=>d.status!=='삭제').map(d=>{const copy=Object.assign({},d);delete copy._row;return copy;}),status:apiStatus()};}
function apiSave(payload){
  if(!payload || !payload.doc || !Array.isArray(payload.items) || payload.items.length>150)throw new Error('저장할 데이터가 올바르지 않습니다.');
  const lock=LockService.getScriptLock();lock.waitLock(30000);
  try {
    const d=payload.doc,all=readAll(),existing=all.docs.find(x=>x.id===d.id);
    if(existing && (!d.expectedUpdatedAt || existing.updatedAt!==d.expectedUpdatedAt))throw new Error('다른 저장 또는 수정이 발견됐습니다. 다시 조회한 후 수정해주세요.');
    if(!existing && d.expectedUpdatedAt)throw new Error('원래 문서를 찾지 못했습니다. 다시 조회해주세요.');
    const id=existing?.id || (typeof d.id==='string' && /^[0-9A-Za-z_-]{12,60}$/.test(d.id)?d.id:Utilities.getUuid());
    const now=new Date().toISOString(),date=cleanText(d.date,10),supplier=cleanText(d.supplier,120);
    if(date && !/^20\d\d-\d\d-\d\d$/.test(date))throw new Error('거래일 형식을 확인해주세요.');
    if(!['미확인','영수증','거래명세서','기타'].includes(d.type))throw new Error('문서 유형이 올바르지 않습니다.');
    if(!['미확인','미지급','지급완료'].includes(d.payment))throw new Error('결제 상태가 올바르지 않습니다.');
    const values=payload.items.map(x=>({id:Utilities.getUuid(),name:cleanText(x.name,150),spec:cleanText(x.spec,80),unit:cleanText(x.unit,40),quantity:checkedNumber(x.quantity),unitPrice:checkedNumber(x.unitPrice),amount:checkedNumber(x.amount)}));
    let photoId=existing?.imageId||'',photoName=existing?.imageName||'';
    if(payload.image){const bytes=b64bytes(payload.image);const fileName=cleanText(payload.image.name||'영수증.jpg',150);
      const f=multipartUpload({name:fileName,mimeType:payload.image.mime,parents:[all.store.folder]},bytes,payload.image.mime,false);
      photoId=f.id;photoName=fileName;
    }
    const row=[id,date,supplier,d.type,checkedNumber(d.supply),checkedNumber(d.tax),checkedNumber(d.total),d.payment,cleanText(d.memo,1500),photoId,photoName,cleanText(d.relatedId,80),existing?.createdAt||now,now,'정상'];
    const base='https://sheets.googleapis.com/v4/spreadsheets/'+encodeURIComponent(all.store.id)+'/values/';
    if(existing){jsonApi(base+encodeURIComponent('Documents!A'+existing._row+':O'+existing._row)+'?valueInputOption=RAW','put',{values:[row]});}
    else jsonApi(base+encodeURIComponent('Documents!A:O')+':append?valueInputOption=RAW&insertDataOption=INSERT_ROWS','post',{values:[row]});
    if(existing){const deactivations=[];for(let i=1;i<all.itemRows.length;i++){
      if(String(all.itemRows[i][1]||'')===id && String(all.itemRows[i][8]||'').toUpperCase()!=='FALSE'){
        deactivations.push({range:'Items!I'+(i+1)+':J'+(i+1),values:[['FALSE',now]]});
      }
    }if(deactivations.length)sheetsBatch(all.store.id,deactivations);}
    if(values.length)jsonApi(base+encodeURIComponent('Items!A:J')+':append?valueInputOption=RAW&insertDataOption=INSERT_ROWS','post',{
      values:values.map(x=>[x.id,id,x.name,x.spec,x.unit,x.quantity,x.unitPrice,x.amount,'TRUE',now])
    });
    return {id:id,updatedAt:now,photoId:photoId};
  }finally{lock.releaseLock();}
}
function apiDelete(id,expectedUpdatedAt){
  const lock=LockService.getScriptLock();lock.waitLock(30000);
  try {const all=readAll(),d=all.docs.find(x=>x.id===id);if(!d)throw new Error('문서가 없습니다.');
    if(d.updatedAt!==expectedUpdatedAt)throw new Error('자료가 변경됐습니다. 새로고침 후 다시 시도하세요.');
    sheetsBatch(all.store.id,[{range:'Documents!N'+d._row+':O'+d._row,values:[[new Date().toISOString(),'삭제']]}]);
    return {ok:true};
  }finally{lock.releaseLock();}
}
function apiImage(id){
  const all=readAll();if(!all.docs.some(d=>d.imageId===id && d.status!=='삭제'))throw new Error('이 장부에 연결되지 않은 사진입니다.');
  const meta=jsonApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(id)+'?fields=mimeType,name');
  if(!/^image\/(jpeg|png|webp|gif)$/.test(meta.mimeType))throw new Error('지원하지 않는 원본 형식입니다.');
  const response=fetchApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(id)+'?alt=media');
  const bytes=response.getContent();if(bytes.length>MAX_IMAGE_BYTES)throw new Error('사진이 너무 큽니다. 구글 드라이브에서 확인해주세요.');
  return {data:Utilities.base64Encode(bytes),mime:meta.mimeType,name:meta.name};
}

/** A snapshot copies only the spreadsheet; original photos remain in the app-owned Drive folder. */
function backupCurrent_(tag) {
  const id=getStore().id,root=PROP.getProperty('ROOT_FOLDER_ID'),created=new Date().toISOString();
  const name='식자재 장부 '+tag+' '+created.slice(0,19).replace(/[T:]/g,'-');
  const copied=jsonApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(id)+'/copy?fields=id,name','post',{
    name:name,parents:[root]
  });
  const backups=JSON.parse(PROP.getProperty('BACKUPS')||'[]');
  backups.unshift({id:copied.id,name:copied.name,createdAt:created});
  PROP.setProperty('BACKUPS',JSON.stringify(backups.slice(0,30)));
  return {id:copied.id,name:copied.name,url:'https://docs.google.com/spreadsheets/d/'+copied.id+'/edit'};
}
function apiBackup() {
  const lock=LockService.getScriptLock();lock.waitLock(30000);
  try{return {backup:backupCurrent_('백업'),status:apiStatus()};}
  finally{lock.releaseLock();}
}
function apiRestoreBackup(id) {
  const lock=LockService.getScriptLock();lock.waitLock(30000);
  try{
    const backups=JSON.parse(PROP.getProperty('BACKUPS')||'[]'),selected=backups.find(x=>x.id===id);
    if(!selected)throw new Error('이 앱에서 만든 백업을 선택하세요.');
    if(getStore().id===id)throw new Error('현재 시트와 동일한 백업입니다.');
    backupCurrent_('복원직전보존');
    // Never edit the snapshot in-place: activate an independent copy.
    const restored=jsonApi('https://www.googleapis.com/drive/v3/files/'+encodeURIComponent(id)+'/copy?fields=id,name','post',{
      name:'식자재 장부 복원 '+new Date().toISOString().slice(0,19).replace(/[T:]/g,'-'),parents:[PROP.getProperty('ROOT_FOLDER_ID')]
    });
    PROP.setProperty('SPREADSHEET_ID',restored.id);
    return apiStatus();
  }finally{lock.releaseLock();}
}

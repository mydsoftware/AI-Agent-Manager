/** کلاینت مرکزی API برای UI. */
const API = {
    baseUrl: '',
    get apiKey() { return localStorage.getItem('ai_agent_api_key') || ''; },
    set apiKey(value) { localStorage.setItem('ai_agent_api_key', value); },
    async call(endpoint, method='GET', data=null) {
        const headers={'Content-Type':'application/json'};
        if(this.apiKey) headers['X-API-Key']=this.apiKey;
        const options={method,headers};
        if(data && method!=='GET') options.body=JSON.stringify(data);
        const response=await fetch(`/api/proxy${endpoint}`,options);
        const payload=await response.json().catch(()=>({}));
        if(!response.ok) throw new Error(payload.error || `خطای HTTP ${response.status}`);
        return payload;
    },
    health(){return this.call('/health');},
    execute(request,agent='developer'){return this.call('/execute','POST',{request,agent});},
    audit(url,mode='pre_contract'){return this.call('/execute/website-audit','POST',{request_id:`exec-${Date.now()}`,url,mode,language:'fa'});},
    route(request){return this.call('/route','POST',{request});},
    planWorkflow(request,agent=''){return this.call('/workflow/plan','POST',{request,agent});},
    runWorkflow(request,agent=''){return this.call('/workflow/run','POST',{request,agent});},
    createProject(project){return this.call('/project/create','POST',project);},
    getProject(id){return this.call(`/project/${encodeURIComponent(id)}`);},
    planProjectWorkflow(id){return this.call(`/project/${encodeURIComponent(id)}/workflow/plan`,'POST',{});},
    runProject(id,request='',agent=''){return this.call(`/project/${encodeURIComponent(id)}/run`,'POST',{request,agent});},
    updateProjectStatus(id,status){return this.call(`/project/${encodeURIComponent(id)}/status`,'POST',{status});},
    activity(id){return this.call(`/project/${encodeURIComponent(id)}/activity`);},
    approvals(projectId=''){return this.call(`/approvals${projectId?`?project_id=${encodeURIComponent(projectId)}`:''}`);},
    createApproval(id,action,description){return this.call(`/project/${encodeURIComponent(id)}/approvals`,'POST',{action,description});},
    resolveApproval(id,status){return this.call(`/approvals/${encodeURIComponent(id)}/resolve`,'POST',{status});},
    startSession(id,request){return this.call('/session/start','POST',{session_id:id,request});},
    answerSession(id,answer){return this.call('/session/answer','POST',{session_id:id,answer});},
    getExecution(id){return this.call(`/executions/${encodeURIComponent(id)}`);}
};
function showNotification(message,type='info'){const n=document.createElement('div');n.className=`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${type==='success'?'bg-green-500 text-white':type==='error'?'bg-red-500 text-white':'bg-blue-500 text-white'}`;n.textContent=message;document.body.appendChild(n);setTimeout(()=>n.remove(),3000);}
function copyToClipboard(text){navigator.clipboard.writeText(text).then(()=>showNotification('متن کپی شد','success'));}

export async function GET(){
 const base=process.env.HPC_API_URL;
 if(!base)return Response.json({error:"Backend not configured"},{status:503});
 try{const r=await fetch(base+"/system-status",{headers:{"X-API-Key":process.env.HPC_API_KEY||""},cache:"no-store",signal:AbortSignal.timeout(15000)});
 return new Response(await r.text(),{status:r.status,headers:{"Content-Type":"application/json","Cache-Control":"no-store"}})
 }catch{return Response.json({error:"Backend unavailable"},{status:502})}
}

import {NextResponse} from "next/server";
import {timingSafeEqual} from "node:crypto";
export function proxy(request){
 const user=process.env.HPC_UI_USER;
 const password=process.env.HPC_UI_PASSWORD;
 if(!user||!password)return new NextResponse("Access not configured",{status:503});
 const expected=Buffer.from("Basic "+Buffer.from(user+":"+password).toString("base64"));
 const actual=Buffer.from(request.headers.get("authorization")||"");
 if(actual.length!==expected.length||!timingSafeEqual(actual,expected))return new NextResponse("Authentication required",{status:401,headers:{"WWW-Authenticate":'Basic realm="HPC Research", charset="UTF-8"',"Cache-Control":"no-store"}});
 return NextResponse.next();
}
export const config={matcher:["/((?!_next/static|_next/image|favicon.ico).*)"]};

import test from "node:test";
import assert from "node:assert/strict";
import {serializeHistory,columns} from "../app/history-export.mjs";
const history=[{id:"job-1",created_at:null,payload:{result:{backend:'CPU,"test"',size:16,median_seconds:0.001,gflops:0}}}];
test("JSON preserves original records",()=>assert.deepEqual(JSON.parse(serializeHistory(history,"json")),history));
test("CSV quotes commas, doubles quotes and preserves zero",()=>assert.equal(serializeHistory(history,"csv"),columns.join(",")+'\r\n"job-1","","CPU,""test""","16","","0.001","0",""'));
test("Empty history exports header",()=>assert.equal(serializeHistory([],"csv"),columns.join(",")));
test("Reject unsupported formats",()=>assert.throws(()=>serializeHistory([],"xml")));

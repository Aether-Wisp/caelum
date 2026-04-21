with open(r'd:\1-compitition\waibao\caelum\src\caelum\static\js\caelum.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_body = """body: JSON.stringify({ 
                vuln_type: type, 
                target_env: params.target_env || "mysql",
                bypass_waf: params.waf_bypass || false,
                max_length: params.length || 0,
                encoding: params.encoding || "none"
            })"""

new_body = """body: JSON.stringify({ 
                type: type.toLowerCase().includes("sql") ? "sqli" : type.toLowerCase().includes("xss") ? "xss" : "cmd", 
                difficulty: params.difficulty || "basic",
                count: 1
            })"""

content = content.replace(old_body, new_body)

old_res = """if (res && res.payload) {
                payloadOutput.value = res.payload;
            } else {
                payloadOutput.value = "Failed to generate payload.";
            }"""

new_res = """if (res && res.payloads && res.payloads.length > 0) {
                payloadOutput.value = res.payloads.join("\\n\\n");
            } else {
                payloadOutput.value = "Failed to generate payload.";
            }"""

content = content.replace(old_res, new_res)

with open(r'd:\1-compitition\waibao\caelum\src\caelum\static\js\caelum.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("JS updated!")

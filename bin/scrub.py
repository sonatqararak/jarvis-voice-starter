#!/usr/bin/env python3
"""Scan shareable files without printing matched content. Extra patterns stay outside the kit."""
import argparse,json,pathlib,re,sys
RULES={
 'ip_literals':r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])|(?:[0-9a-f]{1,4}:){3,}[0-9a-f:]+',
 'email_addresses':r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
 'private_key_blocks':r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
 'provider_tokens':r'\b(?:sk-[A-Za-z0-9_-]{20,}|glpat-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b',
 'bearer_secrets':r'Bearer\s+[A-Za-z0-9._-]{20,}',
 'assigned_secrets':r'(?:api[_-]?key|access[_-]?token|password)\s*[=:]\s*[\"\x27]?[A-Za-z0-9_./+-]{16,}',
 'personal_absolute_paths':r'/(?:Users|home)/[A-Za-z0-9._-]+/',
 'session_uuids':r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b'
}
def scan(root,extra=None):
    rules={k:re.compile(v,re.I) for k,v in RULES.items()}
    if extra:rules['private_denylist']=re.compile(pathlib.Path(extra).read_text().strip(),re.I)
    results={k:0 for k in rules};files=0
    for p in sorted(pathlib.Path(root).rglob('*')):
        if not p.is_file() or '.git' in p.parts or '__pycache__' in p.parts:continue
        if p.is_symlink():raise RuntimeError('Symlink in package: '+str(p.relative_to(root)))
        content=p.read_text();files+=1
        for name,rule in rules.items():results[name]+=len(rule.findall(content))
    return {'files_scanned':files,'findings':results,'pass':not any(results.values())}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('root');a.add_argument('--private-patterns');x=a.parse_args()
    result=scan(x.root,x.private_patterns);print(json.dumps(result,indent=2));sys.exit(not result['pass'])

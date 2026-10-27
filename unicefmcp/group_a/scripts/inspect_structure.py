#!/usr/bin/env python3
import json, sys
d=json.load(open(sys.argv[1]))
df=d['data']['dataflows'][0]; print('DATAFLOW', {k:v for k,v in df.items() if k not in('links','names','descriptions')})
ds=d['data']['dataStructures'][0]; comp=ds['dataStructureComponents']
print('DSD',ds['id'],[ (x['id'],x.get('position'),(x.get('localRepresentation') or {}).get('enumeration','').split('=')[-1]) for x in comp['dimensionList']['dimensions']], [x['id'] for x in comp['dimensionList'].get('timeDimensions',[])])
print('ATTRS',[(a['id'],a.get('assignmentStatus'),a.get('attributeRelationship')) for a in comp['attributeList'].get('attributes',[])])
print('MEASURE',comp['measureList']['primaryMeasure']['id'], (comp['measureList']['primaryMeasure'].get('localRepresentation') or {}))
show=set(sys.argv[2:])
for cl in d['data']['codelists']:
    print('  CL',cl['agencyID'],cl['id'],cl['version'],len(cl['codes']), 'partial=',cl.get('isPartial'))
    if cl['id'] in show:
        for c in cl['codes'][:60]: print('      ',c['id'],'|',c.get('name'),'|',(c.get('parent') or ''))
        if len(cl['codes'])>60: print('       ... +',len(cl['codes'])-60)
print('hierarchicalCodelists:',len(d.get('hierarchicalCodelists',[])))

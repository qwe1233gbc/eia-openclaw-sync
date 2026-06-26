import yaml
from pathlib import Path

# === 13-活性炭参数审核 ===
wf13 = {
    'app': {
        'description': '审核活性炭碘值、比表面积、过滤风速、装填量、更换周期、安全设施及废活性炭产生量',
        'icon': '\U0001F9EA',
        'icon_background': '#FFEAD5',
        'mode': 'workflow',
        'name': '13-活性炭参数审核'
    },
    'kind': 'app',
    'version': '0.6.0',
    'workflow': {
        'graph': {
            'nodes': [
                {'id': 'start', 'data': {'type': 'start', 'title': '开始'}},
                {'id': 'extract', 'data': {
                    'type': 'code', 'title': '提取活性炭相关文本',
                    'code': '# Keywords for text extraction (score-weighted)\n'
                            'KEYWORDS = [\n'
                            '    ("活性炭|颗粒炭|蜂窝炭|纤维炭|吸附", 38),\n'
                            '    ("碘值|比表面积|800mg|650mg|900m", 36),\n'
                            '    ("过滤风速|停留时间|0.5m/s|1.2m/s|0.15m/s", 36),\n'
                            '    ("装填量|装填厚度|300mm|600mm|2.8m", 34),\n'
                            '    ("更换周期|更换频次|吸附容量|10%|S=", 36),\n'
                            '    ("废活性炭|HW49|900-039|危废", 32),\n'
                            '    ("压差计|温度传感器|防火阀|报警|70C|83C", 28),\n'
                            '    ("水喷淋|干式过滤|预处理|降温|除湿", 24),\n'
                            '    ("治理效率|处理效率|净化效率|去除率", 28),\n'
                            ']\n'
                            'SECTION_STARTS = ["运营期","废气","主要环境影响和保护措施","环保工程","污染防治措施"]\n'
                            'SECTION_ENDS = ["废水","噪声","固体废物","环境风险","环境保护措施监督检查清单"]\n'
                            'MAX_LEN = 50000\n'
                }},
                {'id': 'review', 'data': {
                    'type': 'llm', 'title': '审核活性炭参数',
                    'prompt': '你是环评审核专家。审核活性炭治理设施参数:\n'
                              '1.碘值:颗粒炭>=800mg/g,蜂窝>=650mg/g(HJ 2026-2013)\n'
                              '2.过滤风速:颗粒<0.5m/s,蜂窝<1.2m/s,停留时间>=0.5s\n'
                              '3.装填量:>=2.8m3/万m3/h,炭层>=300mm\n'
                              '4.更换周期:T=MxS/(Cx10-6xQxt),S=10%\n'
                              '5.废活性炭:年产生量=装填量x更换次数+吸附量,HW49\n'
                              '6.安全设施:压差计+温度传感器+防火阀\n'
                              '7.预处理:水喷淋+干式过滤,温度<40C,湿度<80%\n'
                              '8.治理效率:单级50-75%,不得简单相加\n'
                              '输出JSON:{"conclusion":"","findings":[],"missing_params":[],"review_comment":""}'
                }},
                {'id': 'end', 'data': {'type': 'end', 'title': '输出结果'}},
            ],
            'edges': [
                {'source': 'start', 'target': 'extract'},
                {'source': 'extract', 'target': 'review'},
                {'source': 'review', 'target': 'end'},
            ]
        }
    }
}

# === 14-危险废物识别审核 ===
wf14 = {
    'app': {
        'description': '审核危废识别完整性、贮存规范性、处置合规性及一般固废管理',
        'icon': '☢',
        'icon_background': '#FFEAD5',
        'mode': 'workflow',
        'name': '14-危险废物识别审核'
    },
    'kind': 'app',
    'version': '0.6.0',
    'workflow': {
        'graph': {
            'nodes': [
                {'id': 'start', 'data': {'type': 'start', 'title': '开始'}},
                {'id': 'extract', 'data': {
                    'type': 'code', 'title': '提取危废固废相关文本',
                    'code': 'KEYWORDS = [\n'
                            '    ("危险废物|危废|HW|900-", 38),\n'
                            '    ("废活性炭|废胶水桶|废机油|废溶剂|废抹布|污泥|废过滤棉", 36),\n'
                            '    ("一般固废|SW|废边角料|废包装|次品", 28),\n'
                            '    ("危废暂存|贮存|防渗|防风|防雨|防晒|防漏", 34),\n'
                            '    ("危废处置|委托|资质|转移联单|处置合同|有资质单位", 32),\n'
                            '    ("危废产生量|t/a|年产生|年处置", 30),\n'
                            ']\n'
                            'SECTION_STARTS = ["固体废物","危险废物","主要环境影响和保护措施"]\n'
                            'SECTION_ENDS = ["环境风险","环境保护措施监督检查清单","结论"]\n'
                            'MAX_LEN = 30000\n'
                }},
                {'id': 'review', 'data': {
                    'type': 'llm', 'title': '审核危废识别与处置',
                    'prompt': '你是环评审核专家。审核危险废物管理:\n'
                              '1.危废识别:是否列出全部?除废活性炭外还应识别废胶水桶/废机油/废溶剂桶/含胶废抹布/废过滤棉等\n'
                              '2.一般固废:废边角料/废包装是否分类,是否说明去向\n'
                              '3.危废贮存:防风防雨防晒防渗漏?液态设围堰?分区存放?\n'
                              '4.危废处置:委托有资质单位?处置能力>=产生量?附转移联单?\n'
                              '5.产生量核对:废活性炭=装填量x更换次数+吸附量\n'
                              '输出JSON:{"conclusion":"","findings":[],"missing_hazards":[],"review_comment":""}'
                }},
                {'id': 'end', 'data': {'type': 'end', 'title': '输出结果'}},
            ],
            'edges': [
                {'source': 'start', 'target': 'extract'},
                {'source': 'extract', 'target': 'review'},
                {'source': 'review', 'target': 'end'},
            ]
        }
    }
}

# === 15-VOCs总量控制审核 ===
wf15 = {
    'app': {
        'description': '审核VOCs总量指标、削减替代方案、低VOCs替代论证及总量一致性',
        'icon': '\U0001F4CA',
        'icon_background': '#FFEAD5',
        'mode': 'workflow',
        'name': '15-VOCs总量控制审核'
    },
    'kind': 'app',
    'version': '0.6.0',
    'workflow': {
        'graph': {
            'nodes': [
                {'id': 'start', 'data': {'type': 'start', 'title': '开始'}},
                {'id': 'extract', 'data': {
                    'type': 'code', 'title': '提取总量控制相关文本',
                    'code': 'KEYWORDS = [\n'
                            '    ("VOCs总量|挥发性有机物总量|排放总量|t/a", 38),\n'
                            '    ("削减替代|减二增一|2:1|替代方案|替代来源", 36),\n'
                            '    ("总量指标|总量控制|总量来源|总量确认", 34),\n'
                            '    ("低VOCs替代|水性替代|不可替代论证|溶剂型", 32),\n'
                            '    ("有组织.*无组织|总VOCs|NMHC|非甲烷总烃", 28),\n'
                            '    ("排放量汇总|总量平衡|污染物排放量汇总", 26),\n'
                            ']\n'
                            'SECTION_STARTS = ["总量控制","主要环境影响和保护措施","环境影响分析"]\n'
                            'SECTION_ENDS = ["环境风险","环境保护措施监督检查清单","结论"]\n'
                            'MAX_LEN = 30000\n'
                }},
                {'id': 'review', 'data': {
                    'type': 'llm', 'title': '审核VOCs总量控制',
                    'prompt': '你是环评审核专家。审核VOCs总量控制:\n'
                              '1.总量指标:是否明确有组织+无组织年排放总量(t/a)?\n'
                              '2.削减替代(顺德区VOCs>=300kg/a):是否2:1替代?来源是否已确认(书面文件)?不得仅写由区统筹\n'
                              '3.低VOCs替代论证:使用溶剂型胶粘剂/油墨/清洗剂是否评估替代可行性?若不可替代是否说明技术原因?\n'
                              '4.总量一致性:源强核算/总量章节/附表中的VOCs数据是否一致?\n'
                              '5.COD/氨氮总量:是否同时明确水污染物总量?\n'
                              '输出JSON:{"conclusion":"","findings":[],"substitution_status":"","review_comment":""}'
                }},
                {'id': 'end', 'data': {'type': 'end', 'title': '输出结果'}},
            ],
            'edges': [
                {'source': 'start', 'target': 'extract'},
                {'source': 'extract', 'target': 'review'},
                {'source': 'review', 'target': 'end'},
            ]
        }
    }
}

# Write all 3
dest = Path('06_Dify工作流')
for name, data in [('13-活性炭参数审核.yml', wf13), ('14-危险废物识别审核.yml', wf14), ('15-VOCs总量控制审核.yml', wf15)]:
    with open(dest / name, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"OK {name}")

print(f"\nDone! 3 workflows in 06_Dify工作流/")

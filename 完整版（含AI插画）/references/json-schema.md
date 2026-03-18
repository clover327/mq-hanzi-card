# JSON Schema 模板

生成字卡时，先输出以下结构的 JSON，再渲染为 HTML。

## 完整 Schema

```json
{
  "char": "",
  "pinyin": "",
  "stroke_count": 0,
  "character_type": "",
  "radical": "",
  "structure": "",
  "age_band": "5-8",
  "frequency_rank": 0,

  "core_origin": "",
  "original_meaning": "",
  "meaning_shift_summary": "",

  "child_story": "",

  "glyph_stages": [
    {
      "stage": "甲骨文",
      "era": "商",
      "description": ""
    },
    {
      "stage": "金文",
      "era": "周",
      "description": ""
    },
    {
      "stage": "小篆",
      "era": "秦",
      "description": ""
    },
    {
      "stage": "楷书",
      "era": "今",
      "description": ""
    }
  ],

  "meaning_journey": [
    {
      "label": "",
      "nodes": ["", "", ""]
    }
  ],

  "character_relations": {
    "word_family": [
      {
        "word": "",
        "gloss": ""
      }
    ],
    "radical_family": {
      "radical": "",
      "meaning_hint": "",
      "examples": ["", "", ""]
    },
    "phonetic_family": {
      "phonetic_component": "",
      "sound_hint": "",
      "examples": ["", "", ""]
    },
    "etymology_relations": [
      {
        "char": "",
        "relation": "",
        "note": ""
      }
    ],
    "confusable_chars": [
      {
        "char": "",
        "difference": ""
      }
    ]
  },

  "reading_context": {
    "char": "",
    "words": ["", "", ""],
    "sentences": ["", "", ""]
  },

  "recording_ladder": {
    "char": "",
    "word": "",
    "sentence": "",
    "free_speak_prompt": ""
  },

  "interaction_prompts": ["", "", ""],

  "parent_script": ["", "", "", ""],

  "citations": [
    {
      "type": "book",
      "title": "",
      "author": "",
      "note": ""
    }
  ]
}
```

## 字段说明

### 基础信息
- `char`：汉字
- `pinyin`：带声调拼音
- `stroke_count`：笔画数
- `character_type`：造字类型（象形 / 会意 / 形声 / 指事 / 假借）
- `radical`：部首
- `structure`：结构类型（左右 / 上下 / 包围 / 独体 等）
- `age_band`：目标年龄段
- `frequency_rank`：字频排名（从 `hanzi_freq.csv` 查询，共 9901 字）

### 字源信息
- `core_origin`：一句话概括字源核心
- `original_meaning`：本义
- `meaning_shift_summary`：一句话概括意义演变

### 儿童化内容
- `child_story`：80—180 字的字源故事，必须是完整自然段
- `glyph_stages`：字形演变，每阶段一条描述
- `meaning_journey`：意义旅行链，至少 1 条，每条 3—5 个节点

### 关系模块
- `character_relations.word_family`：高频词族，2—5 个
- `character_relations.radical_family`：偏旁家族，含偏旁、意义提示、例字
- `character_relations.phonetic_family`：声旁家族，含声旁、读音提示、例字
- `character_relations.etymology_relations`：字源亲戚字，1—3 个，含关系说明
- `character_relations.confusable_chars`：易混字，1—3 组，含区别说明

不适用时保留空结构（空字符串 + 空数组），不要删除字段。

象形字 / 会意字的 `phonetic_family` 可以为空。
非形声字不要硬造声旁家族。

### 教学模块
- `reading_context`：字、词、句三级阅读阶梯
- `recording_ladder`：录音朗读任务（字、词、句、自由表达提示）
- `interaction_prompts`：亲子互动任务，1—3 条
- `parent_script`：爸妈带法步骤，3—4 步，必须是可执行动作

### 资源与来源
- `citations`：来源说明，至少包含左民安和魏老师

## 填写规则

1. 所有字段都必须填写
2. `child_story` 必须是完整段落，不是几个关键词
3. `word_family` 优先高频词
4. `radical_family` 和 `phonetic_family` 不要乱填；不适用时保留空值
5. `etymology_relations` 只保留最有教学价值的，来源可参考左民安
6. `confusable_chars` 只保留最常见、最值得提醒的
7. `parent_script` 必须是行动步骤，不要空泛教育口号
8. `reading_context.sentences` 必须生活化、口语化、适合朗读

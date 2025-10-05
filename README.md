# RailGo API 接口文档

## 概述
本文档包含 RailGo 应用的所有后端 API 接口，适用于开发桌面版本。

---

## 1. 鉴权相关接口

### 1.1 公测版鉴权检查
**用途**: 验证用户公测码和版本有效性

**请求地址**: 
```
GET https://auth.railgo.zenglingkun.cn/api/check/{version}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| version | URL路径 | string | 是 | 应用版本号 |
| userid | Query | string | 是 | 用户QQ号 |
| key | Query | string | 是 | 公测码 |

**响应**:
```json
{
  "valid": boolean
}
```

---

## 2. 应用状态接口

### 2.1 获取应用统计信息
**用途**: 获取访问量、查询次数等统计信息

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/state
```

**响应**:
```json
{
  "visits": number,
  "queries": number
}
```

### 2.2 获取系统公告
**用途**: 获取系统公告信息

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/notice
```

**响应**:
```json
Array<string>
```

### 2.3 获取轮播图
**用途**: 获取首页轮播图URL

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/pic
```

**响应**:
```json
Array<string>
```

### 2.4 记录访问
**用途**: 记录用户访问（无返回数据）

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/visit
```

---

## 3. 数据服务接口

### 3.1 获取数据库下载地址
**用途**: 获取离线数据库文件下载URL

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/api/v1/url/db
```

**响应**:
```json
{
  "url": string
}
```

### 3.2 获取版本信息
**用途**: 获取软件和数据库版本信息

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/api/v1/info
```

**响应**:
```json
{
  "latest_db": number,
  "db": string,
  "latest_pack": number,
  "pack": string
}
```

### 3.3 获取软件下载地址
**用途**: 获取Android应用安装包下载URL

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/api/v1/url/pack/android
```

**响应**:
```json
{
  "url": string
}
```

---

## 4. 车次查询接口

### 4.1 车次预选搜索
**用途**: 车次搜索框下拉提示

**请求地址**: 
```
GET https://data.railgo.zenglingkun.cn/api/train/preselect?keyword={keyword}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| keyword | Query | string | 是 | 车次搜索关键词 |

**响应**:
```json
[
  {
    "numberFull": Array<string>,
    "fromStation": object,
    "toStation": object
  }
]
```

### 4.2 车次详情查询
**用途**: 获取车次详细信息

**请求地址**: 
```
GET https://data.railgo.zenglingkun.cn/api/train/query?train={车次号}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| train | Query | string | 是 | 车次号码 |

**响应**:
```json
{
  "numberKind": string,
  "numberFull": Array<string>,
  "type": string,
  "timetable": [
    {
      "station": string,
      "stationTelecode": string,
      "trainCode": string,
      "arrive": string,
      "depart": string,
      "distance": string,
      "speed": number,
      "day": string
    }
  ],
  "bureauName": string,
  "runner": string,
  "carOwner": string,
  "car": string,
  "rundays": Array<string>,
  "diagram": [
    {
      "train_num": string,
      "from": Array<string>,
      "to": Array<string>
    }
  ]
}
```

### 4.3 站站查询
**用途**: 根据发站和到站查询车次

**请求地址**: 
```
GET https://data.railgo.zenglingkun.cn/api/train/sts_query?from={发站电报码}&to={到站电报码}&date={日期}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| from | Query | string | 是 | 发站电报码 |
| to | Query | string | 是 | 到站电报码 |
| date | Query | string | 是 | 日期(YYYYMMDD) |

**响应**:
```json
[
  {
    "code": string,
    "number": string,
    "numberFull": Array<string>,
    "numberKind": string,
    "timetable": [
      {
        "station": string,
        "stationTelecode": string,
        "arrive": string,
        "depart": string,
        "day": number
      }
    ],
    "rundays": Array<string>,
    "fromPos": number,
    "toPos": number,
    "passTime": string
  }
]
```

---

## 5. 车站查询接口

### 5.1 车站预选搜索
**用途**: 车站搜索框下拉提示

**请求地址**: 
```
GET https://data.railgo.zenglingkun.cn/api/station/preselect?keyword={keyword}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| keyword | Query | string | 是 | 车站名或拼音 |

**响应**:
```json
[
  {
    "name": string,
    "telecode": string,
    "pinyin": string,
    "pinyinTriple": string,
    "type": Array<string>
  }
]
```

### 5.2 车站详情查询
**用途**: 获取车站基本信息和停靠车次

**请求地址**: 
```
GET https://data.railgo.zenglingkun.cn/api/station/query?telecode={电报码}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| telecode | Query | string | 是 | 车站电报码 |

**响应**:
```json
{
  "data": {
    "name": string,
    "telecode": string,
    "pinyin": string,
    "pinyinTriple": string,
    "type": Array<string>,
    "bureau": string,
    "belong": string
  },
  "trains": [
    {
      "code": string,
      "number": string,
      "numberFull": Array<string>,
      "numberKind": string,
      "timetable": [
        {
          "stationTelecode": string,
          "arrive": string,
          "depart": string,
          "stopTime": string
        }
      ]
    }
  ]
}
```

### 5.3 车站大屏数据
**用途**: 获取客运车站实时大屏信息

**请求地址**: 
```
GET https://screen.data.railgo.zenglingkun.cn/station/{车站名}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| 车站名 | URL路径 | string | 是 | 车站名称(去掉"站"字) |

**响应**:
```json
{
  "data": [
    [
      "车次号",
      "始发站", 
      "终到站",
      "开点时间",
      "候车/检票信息",
      "状态"
    ]
  ]
}
```

---

## 6. 动车组查询接口

### 6.1 动车组运行交路查询
**用途**: 查询动车组或车次的运行交路

**请求地址**: 
```
GET https://emu.data.railgo.zenglingkun.cn/{type}/{keyword}
```

**参数**:
| 参数名 | 位置 | 类型 | 必填 | 说明 |
|--------|------|------|------|------|
| type | URL路径 | string | 是 | "emu"(动车组)或"train"(车次) |
| keyword | URL路径 | string | 是 | 动车组号或车次号 |

**响应**:
```json
[
  {
    "date": string,
    "train_no": string,
    "emu_no": string
  }
]
```

### 6.2 动车组配属查询
**用途**: 根据车型或车号查询配属信息

**请求地址**: 
```
POST https://delay.data.railgo.zenglingkun.cn/api/trainAssignment/queryEmu
```

**请求体**:
```json
{
  "type": "trainSerialNumber" | "trainModel",
  "keyword": string,
  "trainCategory": 1,
  "cursor": number,
  "count": number
}
```

**响应**:
```json
{
  "code": 200,
  "data": {
    "data": [
      {
        "trainModel": string,
        "trainSerialNumber": string,
        "bureau": string,
        "department": string,
        "manufacturer": string,
        "remark": string
      }
    ],
    "hasMore": boolean,
    "totalCount": number
  }
}
```

---

## 7. 实时数据接口

### 7.1 正晚点查询
**用途**: 查询车次正晚点信息

**请求地址**: 
```
POST https://delay.data.railgo.zenglingkun.cn/api/trainDetails/queryTrainDelayDetails
```

**请求体**:
```json
{
  "date": string,
  "trainNumber": string,
  "fromStationName": string,
  "toStationName": string
}
```

**响应**:
```json
{
  "data": [
    {
      "stationName": string,
      "delayMinutes": number,
      "status": number,
      "arrivalTime": string,
      "departureTime": string,
      "stopMinutes": number,
      "arrivalDate": string
    }
  ]
}
```

### 7.2 停台检票口查询
**用途**: 查询车次停靠站台和检票口

**请求地址**: 
```
POST https://mobile.12306.cn/wxxcx/wechat/bigScreen/getExit
```

**请求体**:
```json
{
  "stationCode": string,
  "trainDate": string,
  "type": "D" | "A",
  "stationTrainCode": string
}
```

**响应**:
```json
{
  "status": boolean,
  "data": {
    "platform": string,
    "wicket": string
  },
  "errorMsg": string
}
```

---

## 8. 其他服务接口

### 8.1 反馈用户列表
**用途**: 获取反馈贡献者列表

**请求地址**: 
```
GET https://feedback.railgo.dev/api/get_users
```

**响应**:
```json
{
  "users": Array<string>
}
```

### 8.2 动车组图片贡献者
**用途**: 获取图片贡献者QQ号列表

**请求地址**: 
```
GET https://tp.railgo.zenglingkun.cn/api/user
```

**响应**:
```json
{
  "code": 200,
  "data": Array<string>
}
```

### 8.3 动车组图片
**用途**: 获取动车组车型图片

**请求地址**: 
```
GET https://tp.railgo.zenglingkun.cn/api/{车型}.png
```

### 8.4 图标兑换
**用途**: 验证图标兑换码

**请求地址**: 
```
GET https://api.state.railgo.zenglingkun.cn/api/cc?CODE={兑换码}
```

**响应**:
```json
{
  "success": boolean,
  "msg": string
}
```

---

## 通用说明

### 请求头
所有接口默认使用:
```
Content-Type: application/json
```

### 错误处理
- 成功响应: HTTP 200
- 错误响应: 相应的HTTP状态码 + 错误信息

### 数据格式
- 日期格式: YYYYMMDD
- 时间格式: HH:mm
- 编码: UTF-8

### 分页参数
- `cursor`: 起始位置(从0开始)
- `count`: 每页数量
- `hasMore`: 是否还有更多数据
- `totalCount`: 总记录数

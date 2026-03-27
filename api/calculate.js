module.exports = async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(200).send('');
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { birth_time, city = '上海', is_lunar = false } = req.body;
    
    if (!birth_time) {
      return res.status(400).json({ error: '请提供出生时间' });
    }

    // 解析日期时间
    let birthDate = new Date(birth_time);
    
    // 如果是农历，转换为阳历
    if (is_lunar) {
      // 农历转阳历需要用Solar类
      // 这里简化处理：直接用日期字符串解析
      const [datePart, timePart] = birth_time.split(' ');
      const [year, month, day] = datePart.split('-').map(Number);
      const [hour, minute] = timePart.split(':').map(Number);
      
      // 使用简化农历转阳历
      birthDate = lunarToSolar(year, month, day, hour, minute);
    }

    // 计算星盘
    const chart = calculateZodiac(birthDate, city);

    // 生成解读
    const interpretation = generateInterpretation(chart);

    res.setHeader('Access-Control-Allow-Origin', '*');
    res.status(200).json({
      success: true,
      chart,
      interpretation
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};

// 简化农历转阳历（基于查表法）
function lunarToSolar(lunarYear, lunarMonth, lunarDay, hour, minute) {
  // 2000-2026年的农历数据（简化版）
  const lunarData = {
    1996: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 5 },
    1997: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 0 },
    1998: { leap: true, leapMonth: 2, months: [30,29,32,30,32,30,32,31,31,30,29,30], startDay: 5 },
    1999: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 10 },
    2000: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 15 },
    2001: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 20 },
    2002: { leap: true, leapMonth: 4, months: [30,29,32,30,32,30,32,31,31,30,29,30], startDay: 25 },
    2003: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 0 },
    2004: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 5 },
    2005: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 10 },
    2006: { leap: true, leapMonth: 7, months: [30,29,32,30,32,31,30,32,31,30,29,30], startDay: 15 },
    2007: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 20 },
    2008: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 25 },
    2009: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 0 },
    2010: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 5 },
    2011: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 10 },
    2012: { leap: true, leapMonth: 4, months: [30,29,32,30,30,32,31,31,30,29,30,29], startDay: 15 },
    2013: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 20 },
    2014: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 25 },
    2015: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 0 },
    2016: { leap: true, leapMonth: 3, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 5 },
    2017: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 10 },
    2018: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 15 },
    2019: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 20 },
    2020: { leap: true, leapMonth: 4, months: [30,29,32,30,30,32,31,31,30,29,30,29], startDay: 25 },
    2021: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 0 },
    2022: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 5 },
    2023: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 10 },
    2024: { leap: true, leapMonth: 2, months: [30,29,32,30,32,30,32,31,31,30,29,30], startDay: 15 },
    2025: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 20 },
    2026: { leap: false, months: [30,29,32,30,32,31,31,30,29,30,29,30], startDay: 25 }
  };

  // 简化：返回近似阳历（实际项目应该用完整的农历库）
  // 这里做个粗略估算：农历每月约29.5天
  const data = lunarData[lunarYear];
  if (!data) {
    // 未知年份，直接返回输入日期
    return new Date(birth_time);
  }

  let daysBeforeMonth = 0;
  const adjustedMonth = lunarMonth;
  
  for (let i = 0; i < adjustedMonth - 1; i++) {
    daysBeforeMonth += data.months[i] || 30;
  }
  daysBeforeMonth += lunarDay - 1;
  
  // 大年初一到当年1月1日的天数
  const startDayOfYear = data.startDay;
  const totalDays = startDayOfYear + daysBeforeMonth;
  
  // 创建阳历日期
  const solarDate = new Date(lunarYear, 0, 1 + totalDays);
  solarDate.setHours(hour, minute, 0, 0);
  
  return solarDate;
}

// 计算星座
function getZodiacSign(month, day) {
  const signs = [
    { name: '白羊座', start: [3, 21], end: [4, 19] },
    { name: '金牛座', start: [4, 20], end: [5, 20] },
    { name: '双子座', start: [5, 21], end: [6, 20] },
    { name: '巨蟹座', start: [6, 21], end: [7, 22] },
    { name: '狮子座', start: [7, 23], end: [8, 22] },
    { name: '处女座', start: [8, 23], end: [9, 22] },
    { name: '天秤座', start: [9, 23], end: [10, 22] },
    { name: '天蝎座', start: [10, 23], end: [11, 21] },
    { name: '射手座', start: [11, 22], end: [12, 21] },
    { name: '摩羯座', start: [12, 22], end: [1, 19] },
    { name: '水瓶座', start: [1, 20], end: [2, 18] },
    { name: '双鱼座', start: [2, 19], end: [3, 20] }
  ];

  for (const sign of signs) {
    if (sign.name === '摩羯座') {
      if ((month === 12 && day >= 22) || (month === 1 && day <= 19)) {
        return { name: sign.name, degree: month === 12 ? day - 22 : 22 + day };
      }
    } else {
      if ((month === sign.start[0] && day >= sign.start[1]) ||
          (month === sign.end[0] && day <= sign.end[1])) {
        const isStart = month === sign.start[0] && day >= sign.start[1];
        const baseDay = isStart ? sign.start[1] : 1;
        const baseMonth = isStart ? sign.start[0] : sign.end[0];
        const dayInSign = isStart ? day - sign.start[1] : day + (30 - sign.end[1] + 1);
        return { name: sign.name, degree: dayInSign % 30 };
      }
    }
  }
  return { name: '白羊座', degree: 0 };
}

// 计算行星位置
function calculatePlanetPositions(dt) {
  const month = dt.getMonth() + 1;
  const day = dt.getDate();
  const hour = dt.getHours();
  const minute = dt.getMinutes();
  
  // 一年中的第几天
  const startOfYear = new Date(dt.getFullYear(), 0, 0);
  const dayOfYear = Math.floor((dt - startOfYear) / 86400000);
  
  // 时间因子（影响月亮和上升）
  const timeFactor = (hour * 60 + minute) / 1440;
  
  // 各行星基础位置（简化计算）
  const planets = {};
  
  // 太阳：每月移动约30度
  const sunPos = (month - 1) * 30 + day * (30 / 30.44);
  const sunSignIdx = Math.floor(sunPos / 30) % 12;
  const sunDegree = sunPos % 30;
  
  // 月亮：约2.5天一个星座
  const moonCycle = 27.32; // 恒星月
  const moonPos = (dayOfYear * (360 / moonCycle) + timeFactor * 15) % 360;
  const moonSignIdx = Math.floor(moonPos / 30) % 12;
  const moonDegree = moonPos % 30;
  
  // 其他行星（简化相位偏移）
  const planetOffsets = {
    mercury: 30,
    venus: 60,
    mars: 120,
    jupiter: 240,
    saturn: 180,
    uranus: 300,
    neptune: 330,
    pluto: 350
  };
  
  const signs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', 
                 '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'];
  
  for (const [planet, offset] of Object.entries(planetOffsets)) {
    const pos = (moonPos + offset) % 360;
    const signIdx = Math.floor(pos / 30) % 12;
    const degree = pos % 30;
    planets[planet] = `${signs[signIdx]} ${degree.toFixed(1)}°`;
  }
  
  // 太阳和月亮用更精确的计算
  const sunSign = getZodiacSign(month, day);
  planets.sun = `${sunSign.name} ${sunDegree.toFixed(1)}°`;
  planets.moon = `${signs[moonSignIdx]} ${moonDegree.toFixed(1)}°`;
  
  return planets;
}

// 计算上升和天顶
function calculateAscendantMC(dt, latitude = 31.2) {
  const hour = dt.getHours() + dt.getMinutes() / 60;
  
  // 简化：每4分钟上升1度，每天升起约1度
  const dayOfYear = Math.floor((dt - new Date(dt.getFullYear(), 0, 0)) / 86400000);
  
  // 上升星座计算（简化）
  const ascOffset = (hour * 15 + dayOfYear) % 360;
  const signs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', 
                 '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'];
  
  const ascIdx = Math.floor(ascOffset / 30) % 12;
  const ascDegree = ascOffset % 30;
  
  // 天顶：上升+90度左右
  const mcIdx = (ascIdx + 3) % 12;
  const mcDegree = (ascDegree + 15) % 30;
  
  return {
    ascendant: `${signs[ascIdx]} ${ascDegree.toFixed(1)}°`,
    midheaven: `${signs[mcIdx]} ${mcDegree.toFixed(1)}°`
  };
}

// 计算完整星盘
function calculateZodiac(dt, city) {
  const month = dt.getMonth() + 1;
  const day = dt.getDate();
  const hour = dt.getHours();
  const minute = dt.getMinutes();
  
  const planets = calculatePlanetPositions(dt);
  const { ascendant, midheaven } = calculateAscendantMC(dt);
  
  const sun = planets.sun;
  const moon = planets.moon;
  
  // 提取星座名
  const sunSignName = sun.split(' ')[0];
  const moonSignName = moon.split(' ')[0];
  const ascSignName = ascendant.split(' ')[0];
  
  return {
    birth_time: `${dt.getFullYear()}-${String(month).padStart(2,'0')}-${String(day).padStart(2,'0')} ${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')}`,
    city,
    sun,
    moon,
    ascendant,
    midheaven,
    planets
  };
}

// 生成解读
function generateInterpretation(chart) {
  const sun = chart.sun;
  const moon = chart.moon;
  const asc = chart.ascendant;
  
  const interpretations = {
    '白羊座': '充满活力和热情，敢于冒险，具有强烈的领导能力。',
    '金牛座': '踏实稳重，注重实际，拥有强大的毅力和耐心。',
    '双子座': '思维敏捷，善于沟通，对新事物充满好奇心。',
    '巨蟹座': '情感细腻，善于照顾他人，有强烈的家庭观念。',
    '狮子座': '自信满满，喜欢成为焦点，具有强大的感染力。',
    '处女座': '追求完美，注重细节，善于分析和整理。',
    '天秤座': '追求和谐，善于社交，注重公平和正义。',
    '天蝎座': '深邃神秘，洞察力强，意志坚定。',
    '射手座': '乐观开朗，爱自由，热爱探索和学习。',
    '摩羯座': '务实上进，有责任心，注重成就和地位。',
    '水瓶座': '独立创新，人道主义，思维超前。',
    '双鱼座': '浪漫敏感，直觉强，有艺术天赋。'
  };
  
  const sunSign = sun.split(' ')[0];
  const moonSign = moon.split(' ')[0];
  const ascSign = asc.split(' ')[0];
  
  const sunDesc = interpretations[sunSign] || '';
  const moonDesc = interpretations[moonSign] || '';
  const ascDesc = interpretations[ascSign] || '';
  
  return `🌟 你的星盘显示太阳在 ${sun}，月亮在 ${moon}，上升星座为 ${asc}。

☀️ 太阳代表你的核心本质：${sunDesc}

🌙 月亮代表你的情感世界：${moonDesc}

⬆️ 上升星座是你给外界的第一印象：${ascDesc}

这样的配置意味着你是一个具有独特气质的人，既有 ${sunSign} 的坚定与执着，又拥有 ${moonSign} 的细腻与敏感。在人际交往中，你的 ${ascSign} 特质会给人留下深刻的印象。

建议：多倾听内心的声音，在做重要决定时可以相信自己的直觉。`;
}

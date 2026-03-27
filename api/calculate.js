module.exports = async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    return res.status(200).setHeaders({
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }).send('');
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { birth_time, city = '上海' } = req.body;
    
    if (!birth_time) {
      return res.status(400).json({ error: '请提供出生时间' });
    }

    // 解析日期
    const dt = new Date(birth_time);
    const month = dt.getMonth() + 1;
    const day = dt.getDate();
    const seed = Math.floor((dt - new Date(dt.getFullYear(), 0, 0)) / 86400000);
    
    const signs = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', 
                   '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'];
    
    const sunSign = signs[(month - 1) % 12];
    const moonSign = signs[Math.floor((seed % 29.5) / 2.5) % 12];
    const ascSign = signs[(month + 1) % 12];

    const chart = {
      birth_time,
      city,
      sun: `${sunSign} ${seed % 30}°`,
      moon: `${moonSign} ${(seed * 2) % 30}°`,
      ascendant: `${ascSign} ${(seed * 3) % 30}°`,
      midheaven: `${signs[(month + 4) % 12]} ${(seed * 4) % 30}°`,
      planets: {
        sun: `${sunSign} ${seed % 30}°`,
        moon: `${moonSign} ${(seed * 2) % 30}°`
      }
    };

    const interpretation = `🌟 你的星盘显示太阳在 ${sunSign}，月亮在 ${moonSign}，上升星座为 ${ascSign}。

太阳代表你的核心本质，月亮代表你的情感世界，上升星座则是你给外界的第一印象。

这样的配置意味着你是一个脚踏实地、注重实际的人，同时也拥有丰富的内心世界。`;

    res.status(200).setHeaders({ 'Access-Control-Allow-Origin': '*' }).json({
      success: true,
      chart,
      interpretation
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
};

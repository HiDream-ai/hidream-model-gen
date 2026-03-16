# Vivago AI 模板分类与测试计划

**生成时间**: 2026-03-06  
**总模板数**: 181

---

## 📊 按端口类型分类

### 🖼️ 图片编辑类 (静态特效)

**端口**: image_edit_gen  
**结果类型**: 图片  
**数量**: 17个  
**测试状态**: ✅ 全部完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Motorcycle Boy | ✅ 已测试 |
| 2 | Nine Grid Pet | ✅ 已测试 |
| 3 | Dinner Party | ✅ 已测试 |
| 4 | Midnight Neon | ✅ 已测试 |
| 5 | Domineering CEO | ✅ 已测试 |
| 6 | White Sweater | ✅ 已测试 |
| 7 | Elegant Gentle | ✅ 已测试 |
| 8 | Costume Change | ✅ 已测试 |
| 9 | Lens Heartbeat | ✅ 已测试 |
| 10 | Darkroom Flash | ✅ 已测试 |
| 11 | Noble Person | ✅ 已测试 |
| 12 | Night Chat | ✅ 已测试 |
| 13 | Polaroid | ✅ 已测试 |
| 14 | Black Rose | ✅ 已测试 |
| 15 | Advanced Image | ✅ 已测试 |
| 16 | Cool Boss | ✅ 已测试 |
| 17 | Three Frames | ✅ 已测试 |

**适用场景**: 静态图片编辑、风格转换、肖像增强

---

### 🎬 Proto Transformer (视频特效)

**端口**: proto_transformer  
**结果类型**: 视频  
**数量**: 58个  
**测试状态**: 8/58 完成

#### 已测试 (8个)
| 模板名称 | 状态 | 备注 |
|----------|------|------|
| Mystic Traveler | ✅ | 正常 |
| Autumn Feast | ✅ | 正常 |
| Moving Figure | ✅ | 正常 |
| 1960s Elegant | ✅ | 正常 |
| Doodle Alive | ✅ | 正常 |
| 1970s | ✅ | 正常 |
| A Family | ✅ | 正常 |
| DADADA | ✅ | 新增测试 |

#### 待测试 (50个)
##### 时间/年代风格类
- 1930s vintage style
- 1940s suit portrait
- 1960s Elegant
- 1970s
- 1970s disco
- 1990s Punk Rock
- 2000s Y2K
- 2000s_butterfly
- 1950s
- 1980s_dress

##### 艺术/创意效果类
- Renovation of old photos
- Color the Lines
- Me in Hand
- MUSIC BOX
- Turkey Chasing 🔴
- Little Turkey 🔴
- Painting Style
- Ghost Shadow

##### 魔法/奇幻类
- Magic Reveal (Ravenclaw)
- Magic Reveal (Gryffindor)
- Magic Reveal (Hufflepuff)
- Magic Reveal (Slytherin)

##### 情感/人物类
- Animal Cooking
- With Deceased
- Garden Lover
- Goodnight Kiss
- Hold Deceased
- Boyfriend
- Heavenly Hug 🔴

##### 其他
- Pixar Style
- Molding clay
- Building Character
- 100% Anime
- Pregnant
- Squish it
- Long hair
- ... (更多)

**特殊标记**:
- 🔴 2000s_y2k: 🚫 内容违规（需更换样本重测）
- 🔴 Turkey Chasing, Little Turkey, Heavenly Hug: prompt乱码

---

### 🎬 Video Diffusion Img2Vid

**端口**: video_diffusion_img2vid  
**结果类型**: 视频  
**数量**: 53个  
**测试状态**: 0/53 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Static Shot | ⏳ 待测试 |
| 2 | Ash out | ⏳ 待测试 |
| 3 | Paparazzi Rush | ⏳ 待测试 |
| 4 | Girlfriend's Rose | ⏳ 待测试 |
| 5 | Eye of the Storm | ⏳ 待测试 |
| ... | ... | ... |
| 53 | Fighting Giant 🔴 | ⏳ 待测试 (prompt乱码) |

**适用场景**: 图片转视频、动态效果

---

### 🎬 Video Diffusion Template

**端口**: video_diffusion_template  
**结果类型**: 视频  
**数量**: 12个  
**测试状态**: 0/12 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Shake It Down | ⏳ 待测试 |
| 2 | Kiss Kiss | ⏳ 待测试 |
| 3 | Hip Twist | ⏳ 待测试 |
| 4 | Jiggle Jiggle | ⏳ 待测试 |
| 5 | Shaking | ⏳ 待测试 |
| ... | ... | ... |

---

### 🎬 Avatar Transformer

**端口**: avatar_transformer  
**结果类型**: 视频  
**数量**: 15个  
**测试状态**: 0/15 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Barbie | ⏳ 待测试 |
| 2 | Jungle Reign | ⏳ 待测试 |
| 3 | The Final Professional | ⏳ 待测试 |
| 4 | Wings of Divinity | ⏳ 待测试 |
| 5 | Phoenix Warrior | ⏳ 待测试 |
| ... | ... | ... |

---

### 🎬 Outfit Transformer

**端口**: outfit_transformer  
**结果类型**: 视频  
**数量**: 10个  
**测试状态**: 0/10 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Food Product Display | ⏳ 待测试 |
| 2 | Battle | ⏳ 待测试 |
| 3 | Younger Self | ⏳ 待测试 |
| 4 | With Deceased | ⏳ 待测试 |
| 5 | Garden Lover | ⏳ 待测试 |
| ... | ... | ... |

**特殊标记**:
- 🔴 Kiss Hand: prompt乱码

---

### 🎬 宠物舞蹈 (Pet Dance)

**端口**: pet_dance  
**结果类型**: 视频  
**数量**: 4个  
**测试状态**: 0/4 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Christmas Baby | ⏳ 待测试 |
| 2 | Beach Dance | ⏳ 待测试 |
| 3 | Christmas Pet | ⏳ 待测试 |
| 4 | Gentle Pet | ⏳ 待测试 |

---

### 🎬 风格转换 (Style Transformer)

**端口**: style_transformer  
**结果类型**: 视频  
**数量**: 2个  
**测试状态**: 0/2 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Ghibli | ⏳ 待测试 |
| 2 | Ghibli2 | ⏳ 待测试 |

---

### 🎬 人物转换 (Figure Transformer)

**端口**: figure_transformer  
**结果类型**: 视频  
**数量**: 2个  
**测试状态**: 0/2 完成

| # | 模板名称 | 状态 |
|---|----------|------|
| 1 | Glam Cat 🔴 | ⏳ 待测试 (prompt乱码) |
| 2 | Photo Restore | ⏳ 待测试 |

---

## 📋 后续测试建议

### 优先级1: 完成proto_transformer剩余测试
- 重试网络错误的模板
- 更换样本测试违规模板

### 优先级2: 按使用场景分批测试
1. **年代/复古风格**: 1930s, 1940s, 1950s, 1960s, 1970s, 1980s, 1990s, 2000s
2. **节日/主题**: Christmas系列, Halloween系列
3. **宠物**: Pet Dance系列
4. **创意/艺术**: Magic Reveal系列, Painting Style, Anime系列

### 优先级3: 处理乱码模板
等待新的配置文件后重新测试:
- Turkey Chasing
- Turkey Away
- Glam Cat
- Little Turkey
- Heavenly Hug
- Fighting Giant
- Kiss Hand

---

## 📊 测试进度汇总

| 端口类型 | 总数 | 已测试 | 未测试 | 优先级 |
|----------|------|--------|--------|--------|
| image_edit_gen | 17 | 17 | 0 | ✅ 完成 |
| proto_transformer | 58 | 8 | 50 | 🔴 高 |
| video_diffusion_img2vid | 53 | 0 | 53 | 🟡 中 |
| video_diffusion_template | 12 | 0 | 12 | 🟡 中 |
| avatar_transformer | 15 | 0 | 15 | 🟢 低 |
| outfit_transformer | 10 | 0 | 10 | 🟢 低 |
| pet_dance | 4 | 0 | 4 | 🟡 中 |
| style_transformer | 2 | 0 | 2 | 🟢 低 |
| figure_transformer | 2 | 0 | 2 | 🟢 低 |
| 其他 | 8 | 0 | 8 | 🟢 低 |

---

*分类报告由测试脚本自动生成*

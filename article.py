import re
from pyquery import PyQuery as pq

def get_article(originUrl):
  doc = pq(url = originUrl)
  script = doc('script').text()
  # 提取文章封面图, 在script中的var msg_cdn_url里面
  photoUrl = re.findall('msg_cdn_url = "(.*?)";',script)[0]
  # 提取文章标题
  title = doc('#activity-name').text()
  # 提取文字的工作号
  tag = doc('.profile_nickname').text()
  # 移除iframe视频, 因为没法显示视频
  article = doc('#js_content').remove('iframe')
  # 图片的data-src改为src
  imgs = article('img').items()
  for img in imgs:
    src = img.attr('data-src')
    img.attr('src', src)
    img.remove_attr('data-src')
  textContent = '<div class="rich_media_content js_underline_content" id="js_content">'+article.html()+'</div>'
  # 返回数据库中需要的字段
  return tag,title,photoUrl,originUrl,textContent

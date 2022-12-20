import re
from pyquery import PyQuery as pq


def get_cover(doc):
  script = doc('script').text()
  # 提取文章封面图, 在script中的var msg_cdn_url里面
  try:
    photoUrl = re.findall('msg_cdn_url = "(.*?)";', script)
    if len(photoUrl) > 0:
      return photoUrl[0]
    else:
      # 寻找封面
      photoUrl = re.findall('\'(.*?)\'; // 封面', script)
      return photoUrl[0]
  except Exception:
    print('没有找到封面')
    return 

def get_article(originUrl):
  doc = pq(url = originUrl)
  photoUrl = get_cover(doc)

  # 提取文章标题
  title = doc('#activity-name').text()
  # 提取文字的工作号
  tag = doc('.profile_nickname').text()
  # 移除iframe视频, 因为没法显示视频
  article = doc('#js_content').remove('iframe')
  img_list = article.find('#img_list')
  if img_list:
    # 来自分享图片
    tag = doc('#js_account_nickname').text()
    title = '分享图片'
    textContent = '<div class="rich_media_content js_underline_content" id="js_content">'+article.html()+'</div>'
    # 返回数据库中需要的字段
    return tag,title,photoUrl,originUrl,textContent
  if article.text() or article('img'):
    # 图片的data-src改为src
    imgs = article('img').items()
    for img in imgs:
      src = img.attr('data-src')
      img.attr('src', src)
      img.remove_attr('data-src')
    textContent = '<div class="rich_media_content js_underline_content" id="js_content">'+article.html()+'</div>'
    # 返回数据库中需要的字段
    return tag,title,photoUrl,originUrl,textContent
  else:
    # 分享的文章
    print('来之分享的文章')
    link = doc('#js_share_source').attr('data-url')
    return get_article(link)
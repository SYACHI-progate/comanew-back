from PIL import Image, ImageDraw

# 600x400の白いキャンバスを作成
canvas = Image.new('RGB', (600, 300), color='white')

# ImageDrawオブジェクトを作成
draw = ImageDraw.Draw(canvas)

# キャンバス全体に黒い枠を描画
border_width = 2
draw.rectangle([0, 0, 599, 299], outline='black', width=border_width)

# キャラクターの画像を読み込む（画像ファイルが必要です）
character1 = Image.open('char/char1-1.png').convert('RGBA').resize((200, 300))
character2 = Image.open('char/char1-2.png').convert('RGBA').resize((200, 300))
hukidashi1 = Image.open(
    'speak/hukidashi1.png').convert('RGBA').resize((80, 160))
hukidashi2 = Image.open(
    'speak/hukidashi1.png').convert('RGBA').resize((100, 160))
dodon = Image.open(
    'speak/dodon.png').convert('RGBA').resize((50, 80))
# 透過画像を白背景に合成する関数


def paste_transparent(background, foreground, position):
    temp = Image.new('RGBA', background.size, (0, 0, 0, 0))
    temp.paste(foreground, position, foreground)
    return Image.alpha_composite(background.convert('RGBA'), temp).convert('RGB')


# キャラクターを配置
canvas = paste_transparent(canvas, character1, (20, 50))
canvas = paste_transparent(canvas, character2, (370, 50))
canvas = paste_transparent(canvas, hukidashi1, (200, 50))
canvas = paste_transparent(canvas, hukidashi2, (300, 80))
canvas = paste_transparent(canvas, dodon, (260, 0))
# 画像を保存
canvas.save('four_panel_comic_with_border.png')

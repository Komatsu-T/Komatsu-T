import re
import sys

import requests

QIITA_USER_ID = 'tabintone'
PER_PAGE = 100
START_MARKER = '<!-- Qiita_ARTICLES:START -->'
END_MARKER = '<!-- Qiita_ARTICLES:END -->'
README_PATH = './README.md'

def fetch_articles(user_id: str, per_page: int) -> list:
    """Qiita APIから指定ユーザーの記事を取得し、記事のリストを返す"""

    params = {
        'per_page': per_page,
    }

    try:
        response = requests.get(f'https://qiita.com/api/v2/users/{user_id}/items', params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Qiita APIの取得に失敗しました: {e}")
        raise

def build_markdown(articles: list) -> str:
    """記事のリストから必要情報を抽出し、マークダウン形式の文字列に変換する"""

    lines = []
    for article in articles:
        title = article['title']
        url = article['url']
        likes_count = article['likes_count']
        created_at = article['created_at']
        lines.append(f'- [{title}]({url}) :heart: {likes_count} ({created_at[:10]})')
    return '\n'.join(lines)

def update_readme(articles_markdown: str, path: str) -> None:
    """READMEを読み込み、記事一覧を更新して出力する"""

    with open(path, encoding='utf-8') as f:
        readme = f.read()

    new_readme, n_sub = re.subn(
        rf'({START_MARKER}).*?({END_MARKER})',
        rf'\1\n{articles_markdown}\n\2',
        readme,
        flags=re.DOTALL # 改行コードも含めてマッチングさせるために必要
    )

    if n_sub == 0:
        print('READMEの更新が行われませんでした.')
        sys.exit(1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_readme)

def main():
    articles = fetch_articles(QIITA_USER_ID, PER_PAGE)
    articles_markdown = build_markdown(articles)
    update_readme(articles_markdown, README_PATH)

if __name__ == '__main__':
    main()
from pathlib import Path
import os


def get_project_root():
    # pyprojecct.toml 파일을 기준으로 프로젝트 루트를 판단하는 함수
    current = Path.cwd()

    for parent in [current, *current.parents]:
        if (parent / 'pyproject.toml').exists():
            return parent
    raise FileNotFoundError("[프로젝트 루트 판단 실패] pyproject.toml를 찾을 수 없습니다.")


def set_project_root():
    root = get_project_root()
    os.chdir(root)
    return root

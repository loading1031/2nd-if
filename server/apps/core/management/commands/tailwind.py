"""
Tailwind CSS management command.

Usage:
    python manage.py tailwind build    # 프로덕션 빌드 (minified)
    python manage.py tailwind watch    # 개발 모드 (watch)
    python manage.py tailwind          # 기본값: watch
"""
import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Tailwind CSS 빌드 및 watch 모드 실행'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            nargs='?',
            default='watch',
            choices=['build', 'watch'],
            help='build: 프로덕션 빌드, watch: 개발 모드 (기본값)',
        )

    def handle(self, *args, **options):
        action = options['action']
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent

        tailwind_bin = base_dir / 'tailwindcss'
        input_css = base_dir / 'static' / 'css' / 'input.css'
        output_css = base_dir / 'static' / 'css' / 'output.css'

        # tailwindcss 바이너리 확인
        if not tailwind_bin.exists():
            raise CommandError(
                f'tailwindcss 바이너리를 찾을 수 없습니다: {tailwind_bin}\n'
                '다음 명령어로 설치하세요:\n'
                'curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64\n'
                'mv tailwindcss-macos-arm64 tailwindcss\n'
                'chmod +x tailwindcss'
            )

        # 입력 파일 확인
        if not input_css.exists():
            raise CommandError(f'입력 CSS 파일을 찾을 수 없습니다: {input_css}')

        cmd = [str(tailwind_bin), '-i', str(input_css), '-o', str(output_css)]

        if action == 'build':
            cmd.append('--minify')
            self.stdout.write(self.style.SUCCESS('Tailwind CSS 프로덕션 빌드 시작...'))
        else:
            cmd.append('--watch')
            self.stdout.write(self.style.SUCCESS('Tailwind CSS watch 모드 시작... (Ctrl+C로 종료)'))

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise CommandError(f'Tailwind CSS 실행 실패: {e}')
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nTailwind CSS watch 모드 종료'))

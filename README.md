# Codex Personal Skills

Codex App에서 반복적으로 사용하는 개인 스킬을 다른 사용자도 검토·설치할 수 있도록 묶은 공개 배포본입니다.

## 포함된 스킬

| 스킬 | 역할 | 필수 파일 |
| --- | --- | --- |
| `general-review-loop` | Planner가 범위를 정하고 위임·증거 확인·한 번의 fixback/re-review를 관리 | `SKILL.md`, `agents/openai.yaml` |
| `route-developer-review` | Planner·Developer·Review Team 스레드의 증거를 확인하고 다음 작업을 하나만 라우팅 | `SKILL.md`, `agents/openai.yaml`, `references/contracts.md` |
| `refresh-repo-status` | 현재 구현·README·GitHub Issues를 검증된 범위에 맞춰 동기화 | `SKILL.md`, `agents/openai.yaml` |
| `third-party-codex-updater` | 서드파티 Codex 플러그인·스킬 업데이트를 안전 업데이트와 수동 검토로 분류 | `SKILL.md`, `agents/openai.yaml`, `scripts/check_updates.py` |

`agents/openai.yaml`은 Codex App의 스킬 목록에 표시될 이름·설명·기본 호출문을 제공합니다. `references/contracts.md`와 `scripts/check_updates.py`는 각각 라우팅 계약과 updater 실행에 필요한 런타임 파일이므로 제외하면 안 됩니다.
이 배포본의 review·repository-sync·updater 스킬은 외부 상태 변경과 장시간 루프의 자동 선택을 막기 위해 명시 호출 전용입니다.

## 요구 조건

공통:

- Skills를 지원하는 Codex App 또는 Codex CLI
- Git과 Python 3
- 스킬을 설치할 수 있는 사용자 스킬 디렉터리

`general-review-loop` 추가 조건:

- 여러 단계 작업의 범위·권한·완료 기준을 확인할 수 있어야 함
- 스레드나 worktree를 넘나들면 프로젝트 `cwd`, thread ID, branch, `HEAD`를 확인해야 함
- 실제 산출물과 테스트를 읽고 `reported`, `observed`, `not verified`를 구분해야 함
- 한 사이클의 fixback과 동일 범위 재검토 뒤 `PASS`, `NEEDS_WORK`, `BLOCKED` 중 하나로 닫아야 함

`route-developer-review` 추가 조건:

- 동일 프로젝트의 Planner·Developer·Review Team 스레드
- 프로젝트별 `git status`, diff, 테스트, 산출물, 현재 문서에 대한 읽기 권한
- Codex thread 도구가 없으면 실제 전송 대신 준비된 프롬프트와 triage 기록만 생성

`refresh-repo-status` 추가 조건:

- 대상 Git 저장소의 현재 checkout, 원격 default branch, README, 테스트·산출물에 대한 읽기 권한
- GitHub Issues를 확인하려면 GitHub connector 또는 인증된 `gh` CLI
- Issue·README 원격 변경은 사용자가 명시적으로 허용한 범위에서만 수행

`third-party-codex-updater` 추가 조건:

- `gh` CLI와 인증된 GitHub 세션 (`gh auth status`로 확인)
- 네트워크 접근 및 GitHub 저장소 읽기 권한
- 업데이트 대상의 로컬 clone과 `codex plugin` 명령
- 업데이트 대상 저장소를 담는 로컬 workspace 경로

이 저장소에는 `ponytail`, `agency-router`, `codex-fable5` 같은 제3자 플러그인을 복제하지 않습니다. 해당 플러그인은 각자의 공식 배포 경로에서 별도로 설치하고 버전을 관리해야 합니다.

## 설치

```bash
git clone https://github.com/koreaben777/codex-personal-skills.git
cd codex-personal-skills
./install.sh
```

기본 설치 위치는 `${CODEX_HOME:-$HOME/.codex}/skills`입니다. Codex 환경이 `~/.agents/skills`를 사용한다면 다음처럼 지정합니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills" ./install.sh
```

기존 스킬을 덮어쓰려면 먼저 백업·diff를 확인한 뒤 명시적으로 실행합니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills" ./install.sh --force
```

설치 후 새 Codex App 작업을 열거나 앱을 재시작하면 스킬 메타데이터가 다시 검색됩니다. 다음과 같이 명시적으로 호출할 수 있습니다.

```text
$general-review-loop
$route-developer-review
$refresh-repo-status
$third-party-codex-updater
```

## updater 경로 설정

`third-party-codex-updater`는 서드파티 clone을 기본적으로 `~/Documents/Codex` 아래에서 찾습니다. 다른 위치를 사용하면 실행 전에 다음 환경변수를 설정합니다.

```bash
export CODEX_PERSONAL_SKILLS_ROOT="$HOME/path/to/Codex"
export CODEX_SKILLS_DIR="$HOME/.agents/skills"
```

스킬 실행 명령은 설치 위치에 맞춰 다음 파일을 사용합니다.

```bash
python "$CODEX_SKILLS_DIR/third-party-codex-updater/scripts/check_updates.py" --apply-safe
```

`--apply-safe`는 공식·저위험 업데이트만 적용합니다. SkillOpt-Sleep, codebase-memory-mcp, Superpowers, agency-router 등은 기존 정책에 따라 자동 교체하지 않고 수동 검토로 남깁니다. dirty worktree를 삭제하지 않으며 원격 push도 수행하지 않습니다.

## 안전한 사용 원칙

- 개인 세션 원문, 토큰, credential, private key, `.env` 파일은 이 저장소에 넣지 않습니다.
- `general-review-loop`와 `route-developer-review`는 구현 스레드의 최종 답변만 믿지 않고 live repository 증거를 다시 확인합니다.
- `route-developer-review`는 한 번에 `Developer fixback` 또는 `Review Team review` 중 하나만 선택합니다.
- 리뷰 문서는 기존 파일을 덮어쓰지 않고 고유한 timestamp 경로에 저장합니다.
- updater가 만든 clone과 로컬 변경사항은 사용자가 검토하기 전까지 삭제·대체하지 않습니다.

## 공개 저장소 관리

이 저장소는 개인 스킬의 공개 기준점입니다. 변경 시 다음 순서를 권장합니다.

1. 스킬 본문과 의존 파일을 함께 수정
2. `bash -n install.sh`와 `python -m py_compile skills/third-party-codex-updater/scripts/check_updates.py` 실행
3. 개인 경로·credential·세션 원문 검색
4. 압축본을 새로 생성
5. 의도한 파일만 commit하고 GitHub에 push

제3자 플러그인의 라이선스·업데이트 정책은 해당 원격 저장소를 따릅니다. 이 저장소의 MIT 라이선스는 이 저장소에 포함된 개인 스킬 및 보조 파일에 적용됩니다.

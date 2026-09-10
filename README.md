# Codex Personal Skills

Codex App / Codex CLI에서 쓰는 개인 스킬 7개를 검토·설치할 수 있게 묶은 공개 저장소입니다. 검토·저장소 변경 계열 스킬은 명시 호출 전용이며, `aside-workflow`, `pair-agent-sync`, `project-outline-update`는 요청 목적이 명확히 일치할 때 자동으로 선택될 수 있습니다.

## 빠른 시작

```bash
git clone https://github.com/koreaben777/codex-personal-skills.git
cd codex-personal-skills
./install.sh
```

1. 설치 위치는 기본적으로 `~/.codex/skills`입니다. 이미 같은 이름의 스킬이 있으면 설치를 중단하므로 덮어쓰기 걱정 없이 실행해도 됩니다.
2. Codex App을 재시작하거나 새 작업을 열면 스킬 목록에 나타납니다.
3. 필요한 스킬만 채팅에서 호출합니다.

```text
$aside-workflow
$general-review-loop
$pair-agent-sync
$project-outline-update
$route-developer-review
$refresh-repo-status
$third-party-codex-updater
```

설치 확인:

```bash
ls "${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
```

## 어떤 스킬을 쓸까

| 스킬 | 이런 상황에 호출 | 추가로 필요한 것 |
| --- | --- | --- |
| `refresh-repo-status` | 저장소 README와 GitHub Issues를 실제 구현 상태에 맞추고 싶을 때 | `gh` CLI 인증(Issue 다룰 때만) |
| `third-party-codex-updater` | GitHub에서 설치한 제3자 Codex 플러그인·스킬을 안전한 것만 골라 업데이트하고 싶을 때 | `gh` CLI, 네트워크, `codex plugin` 명령 |
| `pair-agent-sync` | Claude Code와 같은 저장소를 번갈아 쓰면서 상대 에이전트가 무엇을 했는지 정리하고 싶을 때 | `~/.claude/projects` 읽기 권한 |
| `project-outline-update` | 프로젝트 개요서·현황 문서를 현재 파일과 이전 작업 근거에 맞춰 갱신하고 싶을 때 | 관련 로컬 자료 읽기 권한; Notion·Claude·goose 자료는 존재할 때만 |
| `aside-workflow` | Aside Browser 작업을 MCP와 CLI 중 어느 경로로 처리할지 안전하게 정하고 싶을 때 | Aside Browser, Aside MCP 또는 `aside` CLI |
| `general-review-loop` | 같은 프로젝트에 Developer·Review Team 스레드가 이미 있고, Planner 입장에서 한 번의 리뷰·fixback 사이클을 닫고 싶을 때 | 기존 Developer·Review Team 스레드 |
| `route-developer-review` | Planner·Developer·Review Team 3역할로 구현 증거 확인, 독립 리뷰, 승인 게이트를 돌리고 싶을 때 | 기존 3역할 스레드 |

혼자 작업하는 일반적인 저장소라면 위 두 개(`refresh-repo-status`, `third-party-codex-updater`)부터 쓰는 것이 가장 부담이 없습니다. 아래 네 개는 각각 외부 도구나 다중 스레드 구성이 전제입니다.

## 설치 위치와 옵션

기본 위치는 `${CODEX_HOME:-$HOME/.codex}/skills`입니다. `~/.agents/skills`를 쓰는 환경이면 경로를 지정합니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills" ./install.sh
```

같은 이름의 스킬이 이미 있으면 설치가 멈춥니다. 기존 사본을 diff로 확인한 뒤 교체하려면 `--force`를 붙입니다.

```bash
CODEX_SKILLS_DIR="$HOME/.agents/skills" ./install.sh --force
```

`install.sh`는 일곱 스킬 디렉터리를 통째로 복사합니다. 스킬 본문 외에 다음 파일이 실행에 필요하므로 일부만 골라 복사할 때도 함께 가져가야 합니다.

| 스킬 | 필수 파일 |
| --- | --- |
| `aside-workflow` | `SKILL.md`, `agents/openai.yaml` |
| `general-review-loop` | `SKILL.md`, `agents/openai.yaml` |
| `pair-agent-sync` | `SKILL.md`, `scan_pair.py` |
| `project-outline-update` | `SKILL.md`, `agents/openai.yaml` |
| `route-developer-review` | `SKILL.md`, `agents/openai.yaml`, `references/contracts.md` |
| `refresh-repo-status` | `SKILL.md`, `agents/openai.yaml` |
| `third-party-codex-updater` | `SKILL.md`, `agents/openai.yaml`, `scripts/check_updates.py` |

### 업데이트

```bash
cd codex-personal-skills
git pull
./install.sh --force
```

`--force`는 이 저장소의 일곱 스킬만 교체하며, 같은 폴더의 다른 스킬은 건드리지 않습니다. 설치본을 직접 수정해 쓰고 있다면 실행 전에 diff를 확인하세요.

### 제거

```bash
skills_dir="${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}"
for s in aside-workflow general-review-loop pair-agent-sync project-outline-update route-developer-review refresh-repo-status third-party-codex-updater; do
  rm -rf "$skills_dir/$s"
done
```

## 요구 조건

공통:

- Skills를 지원하는 Codex App 또는 Codex CLI
- Git, Python 3
- 스킬 디렉터리에 대한 쓰기 권한

스킬별:

**`refresh-repo-status`**

- 대상 Git 저장소의 현재 checkout, 원격 default branch, README, 테스트·산출물 읽기 권한
- GitHub Issues를 확인·정리하려면 GitHub connector 또는 인증된 `gh` CLI
- Issue·README의 원격 변경은 사용자가 명시적으로 허용한 범위에서만 수행

**`third-party-codex-updater`**

- `gh auth status`로 확인되는 인증된 `gh` CLI와 네트워크 접근
- 업데이트 대상의 로컬 clone과 `codex plugin` 명령
- 기본 clone 위치는 `~/Documents/Codex`이며, 다른 위치는 아래 환경변수로 지정

```bash
export CODEX_PERSONAL_SKILLS_ROOT="$HOME/path/to/Codex"
export CODEX_SKILLS_DIR="$HOME/.agents/skills"
python "$CODEX_SKILLS_DIR/third-party-codex-updater/scripts/check_updates.py" --apply-safe
```

`--apply-safe`는 공식·저위험 경로의 업데이트만 적용하고, 나머지는 수동 검토 목록으로 보고합니다. dirty worktree를 삭제하지 않으며 원격 push도 하지 않습니다. 정책 목록은 스킬의 `SKILL.md`에 있으니 자신의 플러그인 구성에 맞게 수정해 쓰면 됩니다.

**`pair-agent-sync`**

- Python 3와 대상 프로젝트 파일·Git 이력 읽기 권한
- Claude Code 세션을 대조하려면 `~/.claude/projects` 읽기 권한
- 동봉된 `scan_pair.py`는 독립 실행 파일이며 별도의 Claude 스킬 설치나 심볼릭 링크가 필요 없음
- 동작 확인: `python3 <설치경로>/pair-agent-sync/scan_pair.py --selftest`

**`aside-workflow`**

- Aside Browser와 로그인된 macOS 사용자 세션
- Codex에 연결된 Aside MCP 또는 `PATH`의 `aside` CLI
- 기존 탭을 조작하기 전에 현재 페이지 상태를 읽을 수 있는 권한

**`project-outline-update`**

- 같은 프로젝트의 로컬 파일, 기존 Codex App 작업, 메모리와 Git 이력을 읽을 수 있는 권한
- Claude Code·goose 세션과 Notion은 로컬 자료 또는 연결이 있을 때만 읽기 전용으로 사용
- 개요서 편집 전에 근거·변경안·제외 항목 표를 제시하고 별도 승인을 받아야 함

**`general-review-loop`**

- 같은 프로젝트(`cwd`, repository/worktree, branch, `HEAD`)에 이미 존재하는 Developer·Review Team 스레드와 그 thread ID
- 새 스레드 생성·fork·subagent 대체 없이 기존 스레드만 재사용하며, 없으면 `BLOCKED`로 멈춤
- 실제 산출물과 테스트를 읽어 `reported`, `observed`, `not verified`를 구분
- 한 사이클의 fixback과 재검토 뒤 `PASS`, `NEEDS_WORK`, `BLOCKED` 중 하나로 종료
- Review Team이 코드 리뷰를 내부 분할할 때만 선택적으로 `open-code-review-delegate` 스킬과 `ocr` CLI를 사용. 없으면 해당 절차를 생략하고 기존 Review Team 스레드가 직접 리뷰

**`route-developer-review`**

- 같은 프로젝트의 Planner·Developer·Review Team 스레드
- 프로젝트별 `git status`, diff, 테스트, 산출물, 현재 문서 읽기 권한
- Codex thread 도구가 없으면 실제 전송 대신 준비된 프롬프트와 triage 기록만 생성
- Review `PASS`와 commit·push·promotion·deploy 권한은 분리해 관리

## 포함하지 않는 것

`ponytail`, `agency-router`, `codex-fable5`, Archify, Graphify, Open Code Review 같은 제3자 플러그인·스킬은 이 저장소에 복제하지 않습니다. 각자의 공식 배포 경로에서 설치하고 버전을 관리하세요. `third-party-codex-updater`는 이런 제3자 설치본을 관리하는 쪽입니다.

## 안전한 사용 원칙

- 개인 세션 원문, 토큰, credential, private key, `.env` 파일은 이 저장소에 넣지 않습니다.
- `pair-agent-sync`가 읽은 대화 원문은 외부로 보내지 않으며, 결과에서 확인된 사실·대화상 주장·미확인을 분리합니다.
- `project-outline-update`는 다른 작업과 문서를 자료로만 취급하고, 개요서 이외의 파일이나 외부 서비스를 변경하지 않습니다.
- `general-review-loop`와 `route-developer-review`는 구현 스레드의 최종 답변만 믿지 않고 live repository 증거를 다시 확인합니다.
- `route-developer-review`는 한 번에 `Developer fixback` 또는 `Review Team review` 중 하나만 선택합니다.
- 리뷰 문서는 기존 파일을 덮어쓰지 않고 고유한 timestamp 경로에 저장합니다.
- updater가 만든 clone과 로컬 변경사항은 사용자가 검토하기 전까지 삭제·대체하지 않습니다.

## 저장소 관리

이 저장소는 개인 스킬의 공개 기준점입니다. 변경 시 권장 순서:

1. 스킬 본문과 의존 파일을 함께 수정
2. `bash -n install.sh`, 스킬 구조 검사, `scan_pair.py --selftest`, Python compile 검사 실행
3. 개인 경로·credential·세션 원문 검색
4. 의도한 파일만 commit하고 push

## 라이선스

이 저장소의 개인 스킬과 보조 파일은 MIT 라이선스를 따릅니다. 제3자 플러그인의 라이선스·업데이트 정책은 각 원격 저장소를 따릅니다.

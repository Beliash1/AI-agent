# Cici — AI აგენტი (backend + frontend)

აგენტული სისტემა ლოკალურ LLM-ზე (Ollama), მეხსიერებით, ქვე-აგენტებით
(researcher / coder / planner / openhands) და React frontend-ით.

## რა შეიცვალა ამ განახლებაში

**მთავარი გასწორება:** `api/agent_routes.py` აქამდე `orchestrator.py`-ს
(ტვინს) საერთოდ არ იძახებდა — პირდაპირ Ollama-ს მიმართავდა, მეხსიერების,
ინსტრუმენტების და დაგეგმვის გარეშე. ახლა `/agent` route რეალურად
`core.orchestrator.run_agent()`-ს იძახებს.

დამატებით:
- **OpenHands ინტეგრაცია** (`agents/openhands_agent.py`,
  `tools/openhands_tool.py`) — ახალი `delegate_openhands` action რთული,
  მრავალფაილიანი საინჟინრო ამოცანებისთვის (`delegate_coder`-ისგან
  განსხვავებით, რომელიც მოკლე, დამოუკიდებელ სკრიპტებზეა გამიზნული).
- ორი დუბლირებული Ollama კლიენტი გაერთიანდა ერთში (`services/ollama.py`).
- ცენტრალური კონფიგი `.env`-ის საშუალებით (`backend/config.py`) — მანამდე
  მისამართები/ლიმიტები რამდენიმე ფაილში ცალ-ცალკე იყო ჩაწერილი.
- დუბლირებული/მკვდარი ფაილები წაშლილია (`memory/store.py` და
  `mcp/client.py` root-ში, `services/ollama_service.py`).
- `workflows/`-ის გატეხილი importები გასწორდა (cwd-კონვენციასთან შესაბამისობაში).
- frontend-ის `lib/api.js` ახლა რეალურად გამოიყენება (მანამდე მკვდარი იყო),
  დამატებულია "ახალი საუბარი" ღილაკი (მეხსიერების გასუფთავება).

## გაშვება

### 1. Ollama

```bash
docker compose up -d ollama webui
ollama pull qwen3:4b
```

### 2. Backend

```bash
cp .env.example .env        # საჭიროებისამებრ დაარედაქტირე
pip install -e . --break-system-packages
cd backend
uvicorn main:app --reload
```

**⚠️ მნიშვნელოვანი:** ყველა backend-ის მოდული absolute import-ებს
იყენებს (`from services.ollama import ...` და ა.შ.), რაც ვარაუდობს, რომ
`backend/` არის სამუშაო დირექტორია გაშვებისას. ანუ `uvicorn` აუცილებლად
`backend/`-იდან უნდა გაუშვა (`cd backend && uvicorn main:app`), არა
repo root-იდან.

გახსენი http://127.0.0.1:8000/docs შესამოწმებლად.

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

გახსენი http://localhost:5173

## OpenHands ინტეგრაცია (არასავალდებულო)

`delegate_openhands` action-ს სჭირდება ცალკე, დამოუკიდებლად გაშვებული
[OpenHands Agent Server](https://github.com/OpenHands/OpenHands). Cici
მასთან მხოლოდ HTTP-ით საუბრობს (`backend/tools/openhands_tool.py`) —
თავად OpenHands-ს არ უშვებს.

1. გაუშვი OpenHands (`docker-compose.yml`-ში კომენტარშია მაგალითი, ან
   იხ. ოფიციალური quickstart: https://github.com/OpenHands/OpenHands).
2. `.env`-ში:
   ```
   OPENHANDS_ENABLED=true
   OPENHANDS_BASE_URL=http://127.0.0.1:3001   # პორტი დამოკიდებულია დაყენებაზე
   OPENHANDS_API_KEY=...                       # თუ დაყენებამ ითხოვა
   ```
3. `qwen3:4b`-ს (ან სხვა Ollama მოდელს) OpenHands-ისთვისაც სჭირდება
   LLM routing — ეს OpenHands-ის საკუთარი კონფიგურაციაა (LiteLLM),
   Cici-ს კოდს არ ეხება.

⚠️ **REST API schema იცვლება ვერსიებს შორის** — თუ `openhands_tool.py`
შენი კონკრეტული ვერსიისთვის არ მუშაობს, გადაამოწმე
`START_ENDPOINT`/სტატუსის ველების სახელები დოკუმენტაციასთან:
https://docs.openhands.dev

⚠️ **უსაფრთხოება:** OpenHands sandbox კონტეინერებს Docker socket-ის
საშუალებით უშვებს — production-ში აუცილებლად წაიკითხე მათი security
guide (Docker-in-Docker იზოლაცია, `SANDBOX_NETWORK_DISABLED` და ა.შ.),
სანამ ამ action-ს რეალურ სერვერზე ჩართავ.

## არქიტექტურა

```
User -> frontend (React)
         |  POST /agent { message, model, session_id }
         v
backend/api/agent_routes.py
         |
         v
backend/core/orchestrator.py   <- "ტვინი" (ReAct loop, MAX_STEPS-მდე)
         |
         +- memory/store.py            (session history, JSON ფაილებში)
         +- agents/researcher_agent.py -> tools/web_tool.py (DuckDuckGo)
         +- agents/coder_agent.py      -> tools/code_tool.py (subprocess + self-correction)
         +- agents/planner_agent.py    (რთული მოთხოვნების დაშლა ნაბიჯებად)
         +- agents/openhands_agent.py  -> tools/openhands_tool.py (გარე OpenHands სერვერი)
```

## ცნობილი შეზღუდვები

- `memory/store.py` ფაილზეა დაფუძნებული (JSON) — კარგია ერთ მანქანაზე
  დეველოპმენტისთვის, production-ში/მრავალ instance-ზე გადადი SQLite ან
  Redis-ზე (ინტერფეისი იგივე დარჩება: `save_turn`/`get_history`).
- `tools/code_tool.py`-ის `run_python_code` subprocess-ში ეშვება, მაგრამ
  სრული sandbox არ არის (ფაილურ სისტემაზე წვდომა არ არის შეზღუდული).
  production-ისთვის დაამატე docker-იზოლირებული კონტეინერი.
- `backend/mcp/client.py` ჯერ კიდევ სტუბია (`NotImplementedError`) —
  MCP სერვერების (GitHub/Slack/Drive) რეალური კავშირი ჯერ არ არის
  დაწერილი, მხოლოდ ჩონჩხი.

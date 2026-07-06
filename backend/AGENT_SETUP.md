# Cici Agent — სტატუსი

ეს ფაილი მანამდე აღწერდა ხელით ინტეგრაციის ნაბიჯებს (`orchestrator.py`,
`agent_routes.py` და ა.შ. ხელით ჩამატება `main.py`-ში). ეს ნაბიჯები
**უკვე შესრულებულია** — `/agent` endpoint რეალურად იძახებს
`core/orchestrator.py`-ს (ReAct loop + მეხსიერება + ქვე-აგენტები).

სრული გაშვების ინსტრუქციისთვის იხ. repo root-ის `README.md`.

## მოკლედ, რა უნდა გახსოვდეს

- **გაშვება:** `cd backend && uvicorn main:app --reload` (არა repo root-იდან —
  ყველა import absolute-ია, `backend/`-ს დაშვებით).
- **კონფიგი:** ყველა ლიმიტი/URL ახლა `.env`-შია (`.env.example` → `.env`),
  არა hardcoded კოდში. იხ. `backend/config.py`.
- **timeout/retries:** `CODE_TIMEOUT_SECONDS`, `CODE_MAX_RETRIES`,
  `MAX_STEPS` — ყველა `.env`-იდან იკონფიგურირება.
- **უსაფრთხოება:** `run_python_code` subprocess-ში ეშვება, მაგრამ სრული
  sandbox არ არის (ფაილურ სისტემაზე წვდომა არ არის დაცული). production-ში
  დაამატე docker-ში იზოლირებული კონტეინერი ან restricted user.
- **მოდელი:** ნაგულისხმევად `.env`-ის `DEFAULT_MODEL`-ს იყენებს
  (default: `qwen3:4b`) — request body-ში `model` ველით შეგიძლია
  სხვა მოდელზეც გადართო.
- **OpenHands:** რთული საინჟინრო ამოცანებისთვის, იხ. README-ს
  "OpenHands ინტეგრაცია" სექცია.

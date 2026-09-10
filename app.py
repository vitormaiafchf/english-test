import json
import streamlit as st

st.set_page_config(page_title="Cambridge English Level Check", page_icon="🎓", layout="centered")

# Carrega o banco de questões
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()
QUESTIONS_PER_PAGE = 10
TOTAL_PAGES = len(questions) // QUESTIONS_PER_PAGE

# Inicializa variáveis de estado
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

st.title("🎓 Teste de Nivelamento de Inglês (CEFR)")
st.write("Responda às questões com atenção. O teste possui 40 itens divididos em 4 etapas.")
st.divider()

if not st.session_state.submitted:
    # Mostra progresso
    st.progress(st.session_state.current_page / TOTAL_PAGES, text=f"Etapa {st.session_state.current_page} de {TOTAL_PAGES}")
    
    # Define o bloco de questões da página atual
    start_idx = (st.session_state.current_page - 1) * QUESTIONS_PER_PAGE
    end_idx = start_idx + QUESTIONS_PER_PAGE
    current_questions = questions[start_idx:end_idx]

    # Exibe as questões
    for q in current_questions:
        st.markdown(f"**Questão {q['id']}** [{q['level']}]: {q['question']}")
        
        # Cria as opções (radio button) e salva no session_state no momento do clique
        st.radio(
            label=f"Opções da questão {q['id']}",
            options=q["options"],
            index=q["options"].index(st.session_state.answers[q["id"]]) if q["id"] in st.session_state.answers else None,
            key=f"q_{q['id']}",
            label_visibility="collapsed",
            on_change=lambda q_id=q['id']: st.session_state.answers.update({q_id: st.session_state[f"q_{q_id}"]})
        )
        st.write("")

    st.divider()

    # Controles de Navegação
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.current_page > 1:
            if st.button("⬅️ Voltar"):
                st.session_state.current_page -= 1
                st.rerun()

    with col3:
        if st.session_state.current_page < TOTAL_PAGES:
            if st.button("Próximo ➡️", type="primary", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()
        else:
            if st.button("Concluir Avaliação 🏁", type="primary", use_container_width=True):
                # Checa se falta responder alguma
                unanswered = [q["id"] for q in questions if q["id"] not in st.session_state.answers]
                if unanswered:
                    st.error(f"Atenção: Você esqueceu de responder algumas questões! Verifique: {unanswered[:5]}...")
                else:
                    st.session_state.submitted = True
                    st.rerun()

else:
    # Cálculo do resultado
    score = 0
    breakdown = []
    for q in questions:
        user_ans = st.session_state.answers.get(q["id"])
        is_correct = (user_ans == q["answer"])
        if is_correct:
            score += 1
        breakdown.append({
            "id": q["id"],
            "level": q["level"],
            "question": q["question"],
            "user": user_ans,
            "correct": q["answer"],
            "is_correct": is_correct,
            "tip": q["tip"]
        })

    # Régua CEFR
    if score <= 10:
        level, desc = "A1 (Iniciante)", "Você compreende e usa expressões cotidianas e frases básicas para necessidades imediatas."
    elif score <= 20:
        level, desc = "A2 (Básico)", "Você se comunica em tarefas simples e de rotina sobre assuntos familiares e diretos."
    elif score <= 30:
        level, desc = "B1 (Intermediário)", "Você compreende pontos principais e lida com a maior parte das situações do dia a dia."
    else:
        level, desc = "B2 (Intermediário Superior)", "Você compreende ideias complexas, argumenta e interage com boa fluência."

    st.success("Avaliação finalizada com sucesso!")
    
    # Adequando a linguagem para os alunos de 11 e 12 anos (crescimento na língua)
    st.header(f"Seu Nível Estimado: **{level}**")
    st.metric("Total de Acertos", f"{score} / 40")
    st.info(f"O que isso significa para o seu crescimento na língua: {desc}")

    st.divider()
    st.subheader("Gabarito Detalhado")
    for item in breakdown:
        status = "✅ Correto" if item["is_correct"] else "❌ Incorreto"
        with st.expander(f"Questão {item['id']} [{item['level']}] — {status}"):
            st.markdown(f"**Pergunta:** {item['question']}")
            st.markdown(f"**Sua resposta:** `{item['user']}`")
            st.markdown(f"**Resposta correta:** `{item['correct']}`")
            st.caption(f"Dica de ouro: {item['tip']}")

    if st.button("Refazer Teste"):
        st.session_state.submitted = False
        st.session_state.answers = {}
        st.session_state.current_page = 1
        st.rerun()

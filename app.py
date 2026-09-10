import json
import streamlit as st

st.set_page_config(page_title="Cambridge English Level Check", page_icon="🎓", layout="centered")

# Carrega o banco de questões
@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

# Inicializa variáveis de estado
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "answers" not in st.session_state:
    st.session_state.answers = {}

st.title("🎓 Teste de Nivelamento de Inglês (CEFR)")
st.write("Responda às questões com atenção. O teste possui 40 itens divididos em 4 etapas.")
st.divider()

if not st.session_state.submitted:
    # Separação por seções (10 por etapa)
    tab1, tab2, tab3, tab4 = st.tabs(["Parte 1 (1-10)", "Parte 2 (11-20)", "Parte 3 (21-30)", "Parte 4 (31-40)"])
    tabs = [tab1, tab2, tab3, tab4]

    with st.form("quiz_form"):
        for i, tab in enumerate(tabs):
            with tab:
                slice_start = i * 10
                slice_end = slice_start + 10
                for q in questions[slice_start:slice_end]:
                    st.markdown(f"**Questão {q['id']}** [{q['level']}]: {q['question']}")
                    current_val = st.session_state.answers.get(q["id"], None)
                    st.session_state.answers[q["id"]] = st.radio(
                        label=f"q_{q['id']}",
                        options=q["options"],
                        index=q["options"].index(current_val) if current_val in q["options"] else None,
                        key=f"radio_{q['id']}",
                        label_visibility="collapsed"
                    )
                    st.write("")

        submitted = st.form_submit_button("Concluir Avaliação", type="primary")

    if submitted:
        # Checa se falta responder alguma
        unanswered = [q["id"] for q in questions if not st.session_state.answers.get(q["id"])]
        if unanswered:
            st.error(f"Você ainda não respondeu a todas as questões! Faltam itens como: {unanswered[:5]}...")
        else:
            st.session_state.submitted = True
            st.rerun()

else:
    # Cálculo do resultado
    score = 0
    breakdown = []
    for q in questions:
        user_ans = st.session_state.answers[q["id"]]
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
        level, desc = "A1 (Iniciante)", "Compreende e usa expressões cotidianas e frases básicas para necessidades imediatas."
    elif score <= 20:
        level, desc = "A2 (Básico)", "Comunica-se em tarefas simples e de rotina sobre assuntos familiares e diretos."
    elif score <= 30:
        level, desc = "B1 (Intermediário)", "Compreende pontos principais de textos e lida com a maior parte das situações do dia a dia."
    else:
        level, desc = "B2 (Intermediário Superior)", "Compreende ideias complexas, argumenta e interage com considerável fluência."

    st.success("Avaliação finalizada com sucesso!")
    st.header(f"Seu Nível Estimado: **{level}**")
    st.metric("Total de Acertos", f"{score} / 40")
    st.info(desc)

    st.divider()
    st.subheader("Gabarito Detalhado")
    for item in breakdown:
        status = "✅ Correto" if item["is_correct"] else "❌ Incorreto"
        with st.expander(f"Questão {item['id']} [{item['level']}] — {status}"):
            st.markdown(f"**Pergunta:** {item['question']}")
            st.markdown(f"**Sua resposta:** `{item['user']}`")
            st.markdown(f"**Resposta correta:** `{item['correct']}`")
            st.caption(f"Explicação: {item['tip']}")

    if st.button("Refazer Teste"):
        st.session_state.submitted = False
        st.session_state.answers = {}
        st.rerun()
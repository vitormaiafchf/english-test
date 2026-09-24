import json
import streamlit as st

# 1. Configuração em modo 'wide' para aproveitar toda a largura da tela do PC
st.set_page_config(
    page_title="Cambridge English Assessment",
    page_icon="🎓",
    layout="wide"
)

# Estilização CSS para criar a caixa de leitura destacada e ergonômica
st.markdown("""
<style>
    .reading-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 24px;
        font-size: 1.12rem;
        line-height: 1.8;
        color: #1e293b;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        position: sticky;
        top: 20px;
    }
    @media (prefers-color-scheme: dark) {
        .reading-box {
            background-color: #1e293b;
            border-color: #334155;
            color: #f1f5f9;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()
levels = ["A1", "A2", "B1", "B2"]
level_labels = {
    "A1": "Parte 1: A1 Starter",
    "A2": "Parte 2: A2 Elementary",
    "B1": "Parte 3: B1 Intermediate",
    "B2": "Parte 4: B2 Upper-Intermediate"
}

if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

st.title("🎓 Cambridge English Assessment (CEFR)")
st.write("Leia o texto atentamente e escolha a melhor opção para completar cada lacuna.")
st.divider()

if not st.session_state.submitted:
    current_lvl = levels[st.session_state.current_step]
    current_questions = [q for q in questions if q["level"] == current_lvl]
    passage = current_questions[0]

    # Barra de Progresso
    st.progress(
        (st.session_state.current_step + 1) / len(levels), 
        text=f"{level_labels[current_lvl]} ({st.session_state.current_step + 1} de {len(levels)})"
    )

    # 2. Divisão em Duas Colunas (Layout Split-Screen)
    col_text, col_questions = st.columns([1.1, 0.9], gap="large")

    # Coluna Esquerda: Texto de Leitura
    with col_text:
        st.subheader(f"📖 Text: {passage['passage_title']}")
        st.markdown(
            f"""
            <div class="reading-box">
                {passage['passage_text']}
            </div>
            """,
            unsafe_allow_html=True
        )

    # Coluna Direita: Questões das Lacunas
    with col_questions:
        st.subheader("✍️ Select the correct options:")
        for q in current_questions:
            st.markdown(f"**Gap ({q['gap_number']}):**")
            st.radio(
                label=f"q_{q['id']}",
                options=q["options"],
                index=q["options"].index(st.session_state.answers[q["id"]]) if q["id"] in st.session_state.answers else None,
                key=f"radio_{q['id']}",
                label_visibility="collapsed",
                on_change=lambda q_id=q['id']: st.session_state.answers.update({q_id: st.session_state[f"radio_{q_id}"]})
            )
            st.write("")

    st.divider()

    # Controles de Navegação
    nav_left, _, nav_right = st.columns([1, 1, 1])
    with nav_left:
        if st.session_state.current_step > 0:
            if st.button("⬅️ Voltar", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()

    with nav_right:
        if st.session_state.current_step < len(levels) - 1:
            if st.button("Próximo ➡️", type="primary", use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()
        else:
            if st.button("Finalizar Teste 🏁", type="primary", use_container_width=True):
                unanswered = [q["id"] for q in questions if q["id"] not in st.session_state.answers]
                if unanswered:
                    st.error("Por favor, preencha todas as lacunas antes de enviar o teste.")
                else:
                    st.session_state.submitted = True
                    st.rerun()

else:
    # Tela de Resultados
    score = sum(1 for q in questions if st.session_state.answers.get(q["id"]) == q["answer"])

    if score <= 6:
        level, desc = "A1 (Iniciante)", "Compreensão de vocabulário básico de rotina e estruturas essenciais."
    elif score <= 12:
        level, desc = "A2 (Básico)", "Boa compreensão de narrativas simples, marcadores temporais e descrições."
    elif score <= 18:
        level, desc = "B1 (Intermediário)", "Capacidade de acompanhar textos informativos, articuladores lógicos e causa/efeito."
    else:
        level, desc = "B2 (Intermediário Superior)", "Domínio sólido de colocações avançadas, estilo formal e nuances lexicais."

    st.success("Avaliação concluída com sucesso!")
    st.header(f"Nível Estimado: **{level}**")
    st.metric("Total de Acertos", f"{score} / {len(questions)}")
    st.info(f"Diagnóstico de evolução: {desc}")

    st.divider()
    st.subheader("Análise Detalhada das Lacunas")
    for q in questions:
        user_ans = st.session_state.answers.get(q["id"])
        is_correct = (user_ans == q["answer"])
        status = "✅ Correto" if is_correct else "❌ Incorreto"
        with st.expander(f"Lacuna ({q['gap_number']}) [{q['level']}] — {status}"):
            st.markdown(f"**Sua escolha:** `{user_ans}`")
            st.markdown(f"**Resposta correta:** `{q['answer']}`")
            st.caption(f"Justificativa: {q['tip']}")

    if st.button("Recomeçar Avaliação"):
        st.session_state.submitted = False
        st.session_state.answers = {}
        st.session_state.current_step = 0
        st.rerun()

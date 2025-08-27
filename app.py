from shiny import App, ui, render
import pandas as pd
import json

# --- 1. DEFINIÇÃO DAS URLS PÚBLICAS EM CSV ---
url_anual = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTWmG0Q2NevZYGjFnbdp6UoKFU2gyNWvn8cXTCtaQFzIihipHX0-wyu6v7oPK95ygZlH9FfpS-0gRtH/pub?output=csv"
url_mensal = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRnMQAOeapM6pl3xrqQnxG82kO490G-_uLjtc7wicRvug8t4-bkaaVRAWgDHD_X0oKGCs8siTjlkYcO/pub?output=csv"

# --- 2. LEITURA DOS DADOS A PARTIR DAS URLS ---
try:
    df_anual = pd.read_csv(url_anual)
except Exception as e:
    print(f"ERRO: Não foi possível carregar o arquivo anual. Erro: {e}")
    df_anual = pd.DataFrame()

try:
    df_mensal = pd.read_csv(url_mensal)
    if "created_at" in df_mensal.columns:
        df_mensal["created_at"] = pd.to_datetime(df_mensal["created_at"])
except Exception as e:
    print(f"ERRO: Não foi possível carregar o arquivo mensal. Erro: {e}")
    df_mensal = pd.DataFrame()

# --- 3. KEYWORDS ---
keywords = []
if not df_anual.empty:
    keywords = [col for col in df_anual.columns if col != "created_at"]
    keywords.sort()

# --- UI ---
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_radio_buttons(
            "periodicidade",
            "Selecione a periodicidade:",
            {"Anual": "Anual", "Mensal": "Mensal"},
            selected="Anual"
        ),
        ui.input_select(
            "keyword_select",
            "Selecione a palavra-chave:",
            {k: k for k in keywords},
            selected="vegan"
        ),
        title="Métricas de Tweets",
        collapsible=True,
        collapsed=False,
    ),
    ui.tags.head(
        ui.tags.script(src="https://code.highcharts.com/highcharts.js")
    ),
    ui.card(
        ui.output_ui("grafico_html"),
        ui.output_ui("grafico_script"),
    ),
    title="Análise de Métricas de Tweets",
)

# --- Server ---
def server(input, output, session):
    @render.ui
    def grafico_html():
        return ui.HTML('<div id="container" style="height: 420px; margin-top:8px;"></div>')

    @render.ui
    def grafico_script():
        kw = input.keyword_select()
        periodicidade = input.periodicidade()
        
        if not kw:
            return

        if periodicidade == "Anual":
            if df_anual.empty:
                return ui.tags.script("console.log('Dados anuais não disponíveis');")
            df = df_anual
            x_vals = df["created_at"].astype(str).tolist()
        else: # Mensal
            if df_mensal.empty:
                return ui.tags.script("console.log('Dados mensais não disponíveis');")
            df = df_mensal
            x_vals = df["created_at"].dt.strftime("%Y-%m").tolist()
        
        series_data = df[kw].tolist() if kw in df.columns else []

        cfg = {
            "chart": {"type": "area"},
            "title": {"text": f"Métricas de Tweets para “{kw}” ({periodicidade})"},
            "xAxis": {"categories": x_vals},
            "yAxis": {"title": {"text": "Quantidade"}},
            "tooltip": {
                "shared": True,
                "crosshairs": True,
                "pointFormat": '<span style="color:{series.color}">●</span> {series.name}: <b>{point.y:,.0f}</b><br/>'
            },
            "plotOptions": {
                "area": {"stacking": None, "marker": {"enabled": False, "symbol": "circle"}}
            },
            "legend": {"enabled": False},
            "series": [{
                "name": kw,
                "data": series_data,
                "color": "#696969",
                "type": "area"
            }],
            "credits": {"enabled": False}
        }

        return ui.tags.script(
            f"""
            (function render() {{
                var go = (typeof Highcharts !== 'undefined') && document.getElementById('container');
                if (!go) {{ setTimeout(render, 50); return; }}
                Highcharts.chart('container', {json.dumps(cfg)});
            }})();
            """
        )

app = App(app_ui, server)

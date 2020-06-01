from rantanplan.core import get_scansion


def test_seguidilla():
    poem = """Que se caiga la torre
    de Valladolid
    como a mí no me coja,
    ¿qué se me da a mí?"""
    output = "seguidilla"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_seguidilla_compuesta():
    poem = """La cebolla es escarcha
    cerrada y pobre:
    escarcha de tus días
    y de mis noches.
    Hambre y cebolla,
    hielo negro y escarcha
    grande y redonda."""
    output = "seguidilla_compuesta"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_chamberga():
    poem = """Hoy ensalzo a Cristóbal,
    pero es tan alto
    que mi pluma no puede
    más levantarlo,
    que el hombre
    es de prendas mayores,
    le vemos
    para todo dispuesto,
    por grande
    no hay favor que no alcance."""
    output = "chamberga"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_seguidilla_gitana():
    poem = """Yo voy como un ciego
    por esos caminos.
    Siempre pensando en la penita negra
    que llevo conmigo."""
    output = "seguidilla_gitana"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_cuareto_lira_a():
    poem = """¡Cuán solitaria la nación que un día
    poblara inmensa gente,
    la nación cuyo imperio se extendía
    del Ocaso al Oriente!"""
    output = "cuarteto_lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_cuareto_lira_b():
    poem = """Fatigada del baile,
    encendido el color, breve el aliento,
    apoyada en mi brazo
    del salón se detuvo en un extremo."""
    output = "cuarteto_lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_estrofa_safica():
    poem = """Dulce vecino de la verde selva,
    huésped eterno del abril florido,
    vital aliento de la madre Venus,
    Céfiro blando."""
    output = "estrofa_sáfica"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_estrofa_safica_1():
    poem = """Bosque de piedras que arrancó la historia
    a las entrañas de la tierra madre,
    remanso de quietud, yo te bendigo,
    mi Salamanca."""
    output = "estrofa_sáfica"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_estrofa_safica_2():
    poem = """Dulce vecino de la verde selva,
    huésped eterno del abril florido,
    vital aliento de la madre Venus,
    Céfiro blando."""
    output = "estrofa_sáfica"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_estrofa_francisco_de_la_torre():
    poem = """Clamó la gente mísera y el cielo
    escondió los clamores y gemidos
    entre los rayos y espantosos truenos
    de tu turbada cara."""
    output = "estrofa_francisco_de_la_torre"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_endecha_real():
    poem = """En un jardín de flores
    había una gran fuente,
    cuyo pilón servía
    de estanque a carpas, tencas y otros peces.
    Únicamente al riego
    el jardinero atiende,
    de modo que entretanto
    los peces, agua en que vivir no tienen."""
    output = "endecha_real"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_estrofa_manriquena():
    poem = """Delio a las rejas de Elisa
    le canta en noche serena
    sus amores.
    Raya la luna, y la brisa
    al pasar plácida suena
    por las flores."""
    output = "estrofa_manriqueña"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_sexteto_lira_a():
    poem = """Suelta al céfiro blando
    ese vellón que luce en tu cabeza,
    verás que, tremolando,
    a cautivar amantes, Lida, empieza,
    y que en cada cabello
    enreda un alma y aprisiona un cuello."""
    output = "sexteto_lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_sexteto_lira_b():
    poem = """Era Fray Juan un viejo capuchino,
    sostén del peregrino,
    brazo del infeliz, pan del hambriento;
    era Fray Juan, el venerable anciano
    el del cerquillo cano,
    la presea mejor de su convento."""
    output = "sexteto_lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_septeto_lira():
    poem = """El ánimo constante
    armado de verdad, mil aceradas,
    mil puntas de diamante
    embota y enflaquece; y desplegadas
    las fuerzas encerradas,
    sobre el opuesto bando
    con poderoso pie se ensalza hollando."""
    output = "septeto_lira"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_ovillejo():
    poem = """¿Quién menoscaba mis bienes?
    Desdenes.
    Y ¿quién aumenta mis duelos?
    Los celos.
    Y ¿quien prueba mi paciencia?
    Ausencia.
    De ese modo, en mi dolencia
    ningún remedio se alcanza,
    pues me matan la esperanza
    desdenes, celos y ausencia."""
    output = "ovillejo"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_aleluya():
    poem = """¡Soria fría, Soria pura,
    cabeza de Extremadura,
    con su castillo guerrero
    arruinado, sobre el Duero;
    con sus murallas roídas
    y sus casas denegridas!"""
    output = "aleluya"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_quinteto():
    poem = """Juegan y beben: mas en bien, sin vicio,
    sin interés y sin exceso: tienen
    del cuarto de Fermín mal en el quicio
    encajada la puerta y se mantienen
    ojo avizor a él por el resquicio."""
    output = "quinteto"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_sexteto():
    poem = """Entre las rocas de la costa alzada
    se oye un extraño hablar, de madrugada,
    de gentes que en la noche vigilaron;
    las barcas, animadas de un deseo,
    tienen un misterioso balanceo,
    y nunca se están quietas en donde las dejaron."""
    output = "sexteto"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_sextilla():
    poem = """Existe una poesía
    sin ritmo ni armonía
    monótona, cansada,
    como una letanía...,
    de que está desterrada
    la pena y la alegría."""
    output = "sextilla"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_septeto():
    poem = """Vengo a mirarte, campo doloroso,
    cuando son triste leña tus encinas,
    cuando en rigores de tu polvo inclinas
    sus mutilados miembros al reposo
    y en las huellas del ciervo sin camino
    se alberga el yerto ruiseñor piadoso
    segado, en pluma tierna, de su trino."""
    output = "septeto"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_septilla():
    poem = """Luz de sueño, flor de mito,
    tu admirable cuerpo canta
    la gracia de Hermafrodito
    con lo aéreo de Atalanta;
    y de tu beldad ambigua
    la evocada musa antigua
    su himno de carne levanta."""
    output = "septilla"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_copla_arte_menor():
    poem = """Un prado de grand llanura
    veía, con tantas flores,
    que sus diversas colores
    ocultavan la verdura,
    odífferas sin messura;
    en torno del qual passava
    un flumen, que lo çercava
    con su muy gentil fondura."""
    output = "copla_arte_menor"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_copla_mixta():
    poem = """Como el profeta recuenta
    que las tronpas judiciales
    surgirán a los mortales
    con estraña sobrevienta;
    bien así todos vinieron
    aquellos que Amor siguieron
    de quien se faze grand cuenta."""
    output = "copla_mixta"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_copla_castellana():
    poem = """Las riquezas son de amar;
    ca syn ellas grandes cosas
    maníficas nin famosas
    non se pueden acabar;
    por ellas son ensalmados
    los señores,
    príncipes e emperadores,
    e sus fechos memorados."""
    output = "copla_castellana"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_novena():
    poem = """Hubo un hombre vizcaíno,
    por nombre llamado Juan,
    peor comedor de pan
    que bebedor de buen vino.
    Humilde de condición
    y de bajos pensamientos,
    de corta dispusición
    y de flaca complisión,
    pero de grandes alientos."""
    output = "novena"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output


def test_decima_antigua():
    poem = """Fylósofo palanciano,
    varón de alta prudencia,
    a quien dio rrica influencia
    el grand planeta diafano;
    yo veo que syempre afano
    por fablar con sabidores,
    lyndos metrificadores;
    a vos, luz de trobadores,
    fablo en modo linpio sano,
    como hermano con hermano."""
    output = "decima_antigua"
    input_poem = get_scansion(poem, rhyme_analysis=True)
    assert input_poem[0]["structure"] == output

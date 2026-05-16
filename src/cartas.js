/**
 * TRAVESSIAS — cartas de mulheres reais
 * Dados das cartas: metadados + páginas de conteúdo HTML
 *
 * Cada entrada tem:
 *   id, numero (romano ou "" para abertura), label (opcional),
 *   nome, saudacao, idade, cidade, foto, epigrafe, assinatura, paginas[]
 *
 * Para adicionar uma nova carta:
 *   1. Copie um BLOCO existente como template.
 *   2. Preencha os campos.
 *   3. Coloque a foto em /fotos/<id>.jpg.
 *   4. Adicione o objeto ao array CARTAS abaixo.
 */

/* ==========================================================================
   BLOCO 01 — DOCUMENTAÇÃO DE FORMATO
   --------------------------------------------------------------------------
   numero === ""   → entrada é a Abertura (Renata Leão, autora). O template
                     usa o campo `label` em vez de "Carta {numero}".
   numero === "I", "II", ... → carta protagonista numerada.
   ========================================================================== */

const CARTAS = [

  /* ========================================================================
     BLOCO 02 — ABERTURA · Renata Leão (autora)
     ======================================================================== */
  {
    id: "renata",
    numero: "",
    label: "Autora",
    tipo: "abertura",
    nome: "Renata Leão",
    saudacao: "Sobre a autora",
    idade: "45 anos · 1981",
    cidade: "Bauru · SP",
    foto: "fotos/renata_leao.jpg",
    epigrafe: "Travessias é sobre mulheres que seguem, que atravessam a própria vida.",
    assinatura: "Renata Leão",
    paginas: [
      `<p class="sem-indent">Eu sou a <em>Renata Leão</em>. Nasci em Bauru, interior de São Paulo, em 1981. Hoje, 2026, com 45 anos.</p>
       <p>Com formação em jornalismo, sou fotógrafa, comunicadora e uma mulher profundamente atravessada pelas histórias que encontro pelo caminho, especialmente a de tantas mulheres com as quais eu tive o privilégio de trocar.</p>
       <p>Há mais de 20 anos trabalho com comunicação, escuta e relações humanas. Ao longo da minha trajetória, compreendi que algumas histórias não querem apenas ser contadas — elas precisam ser acolhidas.</p>
       <p>Na fotografia feminina, encontrei uma forma de transformar imagem em reencontro. Meu trabalho nasceu do desejo de questionar padrões estéticos, ampliar o sentimento de pertencimento e lembrar mulheres de que seus corpos carregam memória, potência e dignidade, mesmo quando o mundo insiste em dizer o contrário.</p>
       <p>A primeira mulher retratada pelas minhas lentes, sob meu olhar e a minha perspectiva, foi minha mãe em 2021, Sheila, aos 65 anos.</p>
       <p class="sem-indent">As cartas deste e-book nasceram da escuta. Escuta de mulheres reais, com suas dores, afetos, ancestralidades, silêncios, perdas e reconstruções, suas conquistas, superações e felicidades.</p>`,

      `<p>Cada texto foi escrito a partir de entrevistas realizadas durante a 1ª edição do Festival MEL — Mulheres em Lutas, em 2025, onde entendi, mais uma vez, que nenhuma travessia é totalmente solitária.</p>
       <p>Escutei nove mulheres cujas histórias enriqueceram minha bagagem de afeto, consciência e percepção de existência. Incluí, então, uma décima carta: a história da minha mãe. Nada faria mais sentido do que trazer para este projeto a mulher que faz parte da minha origem, da minha ancestralidade e do meu primeiro passo na utilização da fotografia como ferramenta de cura — para mim e para ela.</p>
       <blockquote class="citacao">Travessias é sobre isso: mulheres que seguem, que atravessam a própria vida. Mulheres que sustentam outras mulheres. Mulheres que, juntas, criam abrigo enquanto buscam abrigo em outras travessias.</blockquote>
       <p class="sem-indent">Além da fotografia e da comunicação, também estudo gênero, direitos humanos, atenção plena e práticas integrativas — áreas que atravessam minha maneira de olhar o mundo e de me relacionar com as pessoas.</p>
       <p class="sem-indent"><em>Escrevo porque acredito na delicadeza como ferramenta de resistência.</em></p>
       <p class="sem-indent"><em>Fotografo porque acredito que existir também está no direito de ser vista.</em></p>`
    ]
  },

  /* ========================================================================
     BLOCO 02b — PREFÁCIO · texto placeholder (será substituído)
     ======================================================================== */
  {
    id: "prefacio",
    numero: "",
    label: "Prefácio",
    tipo: "prefacio",
    nome: "Prefácio",
    saudacao: "Antes de começar",
    idade: "",
    cidade: "",
    foto: "fotos/renata_leao.jpg",
    epigrafe: "Texto provisório — o prefácio definitivo será inserido em breve.",
    assinatura: "Travessias",
    paginas: [
      `<div class="aviso-provisorio">
         <span class="aviso-tag">Texto provisório</span>
         <span class="aviso-msg">Este prefácio é um placeholder. O texto definitivo será inserido em breve.</span>
       </div>`,

      `<p class="sem-indent">Há livros que começam por um motivo, e este é um deles. <em>Travessias</em> surge do encontro entre escuta, fotografia e palavra — e antes que qualquer carta seja lida, vale dizer alguma coisa sobre como ele nasceu, por que existe, e o cuidado tomado com cada voz reunida nestas páginas.</p>
       <p>As cartas que vêm a seguir não foram inventadas. Foram colhidas em conversas longas, escutadas duas, três vezes, transcritas com pausas, dúvidas, silêncios. O que está escrito aqui é o que essas mulheres escolheram dizer para si mesmas, depois de tudo.</p>
       <p>Travessia, no plural, não é figura de linguagem. É o que cada uma destas dez vidas conta de modo diferente: o passo que se dá quando o chão treme, a margem que se alcança quando ninguém mais espera, a beira que se cruza calada para que outra mulher cruze depois.</p>
       <p>Que este livro seja, antes de tudo, um abrigo. Que cada carta encontre, no leitor ou na leitora, a escuta que ela mereceu desde o começo. E que, ao terminar, fique a sensação de que nenhuma travessia se faz sozinha.</p>
       <blockquote class="citacao">[Aqui entrará o trecho definitivo escolhido para abrir o livro.]</blockquote>`
    ]
  },

  /* ========================================================================
     BLOCO 03 — CARTA I · Ana Claudia
     ======================================================================== */
  {
    id: "ana",
    numero: "I",
    nome: "Ana Claudia",
    saudacao: "Oi, Ana Claudia",
    idade: "56 anos",
    cidade: "",
    foto: "fotos/ana_claudia.jpg",
    epigrafe: "Há muitas Anas Claudias que habitam dentro de mim — e uma delas, grita.",
    assinatura: "Ana Claudia",
    paginas: [
      `<p class="sem-indent">Quanto tempo a gente não se fala. São 56 anos caminhando juntas — todas nós — com todas as nossas emoções. Que bom que você está aqui para contar a nossa história, lembrando de cada parte que habita dentro da nossa alma, da nossa mente e do nosso corpo.</p>
       <p>Foi uma caminhada longa e sinuosa até aqui, mas repleta de amor e resiliência. Nós acreditamos — e o medo e a confiança caminharam lado a lado, se complementando e se equilibrando durante a jornada que ainda persiste.</p>
       <p>Agradeço por juntas, termos usado cada emoção que compõe o nosso Ser de forma sábia, sem nunca perder a essência. Desviamos das leis que se transformaram em instrumentos de terror e vingança, em mãos erradas e narcisistas ao longo do caminho.</p>
       <p>Por um desenho genuíno de família — que foi mal interpretado por um olhar tendencioso e parcial, que fragmentou a convivência do afeto. A convivência física, porque o afeto… esse é onipresente.</p>
       <p class="sem-indent">O Benjamim, hoje com 25 anos, foi desrespeitado como pessoa humana, usado como instrumento de vingança pelo genitor. Mas nós continuamos acreditando no amor, mesmo em meio à desordem social que nos afastou fisicamente por tantos anos.</p>
       <p>Não recorremos do processo. Não tivemos condições emocionais de lutar com o corpo presente. Atravessamos o oceano, nadando contra tudo o que queríamos, para então chegar à superfície e voltar a respirar. O Benjamim só tinha 10 anos… mas sabíamos que, um dia, ele entenderia. O tempo era necessário.</p>
       <p>Às vezes, é preciso se ausentar de si mesma para conseguir enxergar com clareza e recuperar o oxigênio.<br>Somos corajosas!</p>
       <p>Aliás, acredito que essa palavra — <em>coragem</em> — atravessa a nossa história. Quando olho para trás e vejo onde estamos agora… Voltamos. Encontramos o Benjamim.</p>
       <p>Você lembra como foi desafiador tomar essa decisão? A vida estava se ajeitando — porém, sem ele. E a dele estava se desajeitando. Precisava, agora sim, da nossa presença. Corpo presente, cheio de energia e vontade.</p>
       <p class="sem-indent">Fomos parar na vida noturna, lembra? Somos versáteis. A experiência com produção de eventos se uniu àquela carreira mirim que ainda engatinhava rumo a um objetivo legítimo: trabalhar com o que se ama. Ele estava se formando… DJ com 13 anos.</p>
       <p>Essa LAP — Lei de Alienação Parental — nunca foi capaz de nos Alienar, nunca foi capaz de separar a gente, de verdade. Nunca lapidou os nossos sentimentos. Foi apenas um lapso que, como uma lapiseira, serviu igualmente como instrumento de crescimento. Crescemos. Nos fortalecemos. Juntos.</p>`,

      `<p>A LAP… a lei que não devia "pegar". Sabe aquela história: "tem lei que não pega"? Pois é, essa pegou.<br>E agora?</p>
       <p>São muitas outras histórias sendo lapidadas, de muitas outras mulheres, junto com a gente, Ana. Ana Claudia. Anas… Anas Claudias!</p>
       <blockquote class="citacao">Há muitas Anas Claudias que habitam dentro de mim — e uma delas, grita. Grita alto. E há quem escute. Porque esse grito se funde a tantos outros que ecoam, fazendo barulho. Gritamos mais alto que a LAP. Vamos silenciar a LAP. Vamos!</blockquote>
       <p class="sem-indent">Ana Claudia, você tinha 41 anos. Agora, eu estou com 56. Você também, amadurecemos juntas — e agradeço pelo que você fez por nós.</p>
       <p>Todas as suas ações nos trouxeram até aqui.</p>
       <p>Obrigada. Seguimos juntas, como abelhas, como um enxame!!!</p>`
    ]
  },

  /* ========================================================================
     BLOCO 04 — CARTA II · Luiza
     ======================================================================== */
  {
    id: "luiza",
    numero: "II",
    nome: "Luiza",
    saudacao: "Oi, Luiza",
    idade: "25 anos",
    cidade: "Mariana · MG",
    foto: "fotos/luiza.jpg",
    epigrafe: "Nós somos grandes, Luiza. Sempre fomos.",
    assinatura: "Luiza",
    paginas: [
      `<p class="sem-indent">Quanto tempo se passou desde a nossa última conversa… Já são 25 anos de jornada compartilhada. Talvez nem tenhamos tido uma conversa profunda ao longo da nossa evolução.</p>
       <p>Todas nós, lado a lado — com cada emoção sentida no caminho, formamos a Luiza de hoje. Trazemos muitas dentro de nós, não é Luizinha? Hoje, é um alívio e uma alegria poder dar voz a essa história, revisitando cada pedaço que vive em nossa alma, mente e corpo.</p>
       <p>Lembra quando a mamãe trazia para casa muito mais do que histórias de sala de aula? Ela contava sobre histórias desafiadoras das famílias daquelas crianças que deveriam ter como única preocupação, os estudos.</p>
       <p>Ela fazia isso de forma silenciosa, sem buscar mérito ou reconhecimento pelas articulações movimentando inúmeras pessoas em benefício dos que mais precisavam. Obrigada pela criança determinada e pela menina de Mariana que usou o medo como ferramenta de obter coragem pra encarar de frente um ambiente conservador, no interior de Minas Gerais.</p>
       <p class="sem-indent">Foi essa menina que, aos 17 anos, mudou de cidade para estudar administração e construiu as bases que sustentam a mulher que somos hoje. Lembra como foi desafiador? O medo, as novidades, a solidão… Mas também quanta coisa a gente colocou na bagagem! Algumas dessas memórias ainda estão na minha mala.</p>
       <p>Você não imagina onde estamos hoje. São Paulo, acredita? Em um festival feito especialmente para nós, mulheres. Tem tanta coisa bonita acontecendo! Agora, seguimos o legado da mamãe: Levar conhecimento onde o conhecimento insiste em não alcançar!</p>`,

      `<p>São Paulo é uma cidade intensa, aqui tudo está em movimento! Sabe a coragem que você agarrou lá atrás? Hoje vejo que ela começou com a vovó, que foi corajosa e revolucionária para o tempo dela e, junto com o vovô, trabalhou para que os três filhos pudessem estudar, incluindo a mamãe, que é professora e assistente social. Ela varreu muitas ruas abrindo espaço pra gente passar, transformando o lixo em educação.</p>
       <p class="sem-indent">Ah, preciso te contar: em 2020 vivemos uma pandemia. Foi um tempo triste, de muitas perdas. Mas a gente ficou bem. E, justamente nesse período, ganhamos o troféu de Jovens Talentos em Brasília, por um trabalho de comunicação numa campanha política do papai!</p>
       <p>Tivemos tanto cuidado na nossa família. Cuidar. Cuidar de nós e de quantas pessoas pudermos. Esse festival tem me mostrado isso. São muitas mulheres se movimentando para o cuidado com outras mulheres — precisamos umas das outras.</p>
       <p>Estou criando pontes que servirão de irrigação para as nossas raízes mineiras. O ano passado nasceu o Movimento por Mulheres em Mariana e nós fazemos parte disso e vamos fazer ainda mais. Sabe por quê? Não tivemos nenhuma mulher eleita em 2024. Sem mulheres na política não terão políticas públicas voltadas para mulheres.</p>
       <p>Enquanto isso, por aqui, o Hamudes me apoia muito. Estamos juntos há 11 meses. Ele é assessor parlamentar e está lado a lado na caminhada rumo aos nossos objetivos. Nossa régua é alta!</p>
       <p class="sem-indent">Agora, mais do que nunca, quero escancarar as lutas que correm em nosso sangue. A começar pela cor da nossa pele — desafio enfrentado com coragem pela vovó. Uma lição passada com sabedoria.</p>`,

      `<p>Vivemos em uma cidade linda, cheia de história, mas conservadora. Onde vínculos são criados conforme o sobrenome e o saldo bancário. Mas a vovó deu peso à nossa história.</p>
       <blockquote class="citacao">Nós somos grandes, Luiza. Sempre fomos.</blockquote>
       <p>Os preconceitos nunca nos pararam. Nem mesmo quando perdemos um emprego por perseguição política. Sempre que duvidam de nós — especialmente quando é um homem, menos capacitado, que ainda assim ganha mais voz — nossa coragem se inflama. E seguimos. Nós sempre conseguimos.</p>
       <p>Tenho muito orgulho da nossa história, construída com uma rede de apoio gigantesca. E você é a base disso tudo. Uma base firme, que passa por reformas importantes. Reformas que não erguem muros, mas fortalecem a estrutura.</p>
       <p>Obrigada por tudo o que fez por nós até aqui. Agora, deixa comigo. Eu vou fazer um bom trabalho.</p>`
    ]
  },

  /* ========================================================================
     BLOCO 05 — CARTA III · Silvia
     ======================================================================== */
  {
    id: "silvia",
    numero: "III",
    nome: "Silvia",
    saudacao: "Oi, Silvia… Silvinha",
    idade: "57 anos",
    cidade: "Cachoeirinha",
    foto: "fotos/silvia_teixeira.jpg",
    epigrafe: "A Silvinha, pequenina e cheia de culpa, e a Silvia, consciente e plena.",
    assinatura: "Silvia",
    paginas: [
      `<p class="sem-indent">Há quanto tempo a gente não se fala. São 57 anos caminhando juntas — todas nós — com todas as nossas emoções. Que bom que estou aqui para contar a nossa história, lembrando de cada parte que habita dentro da nossa alma, da nossa mente e do nosso corpo.</p>
       <p>Foi uma caminhada permeada pela busca. Busca por novas oportunidades… Oportunidades que nos deram a liberdade de viver as nossas emoções. Liberdade de ter a chance de proporcionar educação e acesso à tantas pessoas que fazem parte da nossa jornada, sinto que somos responsáveis por isso.</p>
       <p>Sabe por quê? Agora, nós podemos, juntas, sermos essa ponte. Uma ponte de conhecimento, amor e confiança. Assim como toda a nossa bagagem foi, e é, a ponte entre nós… A Silvinha, pequenina e cheia de culpa, e a Silvia, consciente e plena dos meus poderes de hoje.</p>
       <p>Nós conseguimos, e eu só estou aqui hoje, no MEL, porque você fez tudo o que tinha que ser feito, antes. Agora, eu posso dizer: Nós temos, nós acreditamos, nós pertencemos. Aliás, obrigada por nunca ter deixado de acreditar.</p>
       <p class="sem-indent">Você foi uma criança privilegiada e me transformou na adulta que te agradece hoje. Obrigada, Silvinha. Nós nos formamos professora, sabia? Sabe a culpa de nunca ter chamado a Lorecy de "mãe"? Não existe mais! Nossa trajetória tinha que ser assim, nós tínhamos que ter passado a infância em meio aos nossos primos militantes para colocar a educadora e a militante para trabalhar. Afinal, somos buscadoras.</p>
       <p>Eu já até me aposentei, da sala de aula, porque continuo vivendo nossa busca com mais energia do que nunca. Aliás, nos desligamos rapidamente do ambiente escolar, porque entendi que a educação estava em outro ambiente, pra nós. Seguimos educando e tocando almas, fazendo com que outras mulheres continuem acreditando, como você e eu.</p>
       <p>Inclusive, estou cheia de orgulho, trago ex-alunas nessa caminhada, na mesma busca de mostrar que sonhos podem ser realizados em qualquer lugar, até mesmo nas periferias. Na busca de levar dignidade para tantas mães, especialmente as atípicas.</p>
       <p class="sem-indent">Nós lutamos para combater a violência contra as mulheres, sabia? Você adoraria ver isso aqui, o MEL está lindo! Mulher em Lutas! Ah, você está aqui, na verdade, junto comigo, se emocionando comigo e levando tantas bandeiras a serem levantadas em Cachoeirinha, onde há tantas mulheres se sentindo sozinhas e impotentes, nadando em cachoeiras de lágrimas.</p>`,

      `<p>Será que a mamãe, Laci, se sentia assim também enquanto lavava suas roupas? De uma coisa eu tenho certeza. Foi ela que nos ensinou e apontou os caminhos que poderíamos seguir. Foi ela que nos ensinou a nadar e que as lágrimas podem não ser de dor. Foi ela que nos transformou em amor.</p>
       <p>Por falar em amor, nós temos uma filha e um neto. É a nossa história sendo contada, é a posteridade.</p>
       <p>Hoje, eu não peço mais desculpas à Lorecy por amar tanto a mamãe e a nossa família. Agora eu entendo, nos libertei dessa culpa. A Loreci foi uma mulher, antes de ser mãe. Ela teve que trabalhar e não pode acompanhar nosso crescimento.</p>
       <p>Por isso estou aqui hoje, nesse estágio da nossa vida, em meio a um enxame de tantas outras mulheres. É isso que me move!</p>
       <p>Obrigada por seguirmos juntas, como abelhas, como enxame!</p>`
    ]
  },

  /* ========================================================================
     BLOCO 06 — CARTA IV · Thainá
     ======================================================================== */
  {
    id: "thaina",
    numero: "IV",
    nome: "Thainá",
    saudacao: "Oi, Thainá",
    idade: "29 anos",
    cidade: "Salvador · BA",
    foto: "fotos/thaina_britto.jpg",
    epigrafe: "Esse corpo que abriga a nossa história.",
    assinatura: "Thainá",
    paginas: [
      `<p class="sem-indent">Há quanto tempo não nos falamos. São 29 anos caminhando juntas — todas nós — com todas as nossas emoções. Que bom que estou aqui para contar a nossa história, lembrando de cada parte que habita nossa alma, nossa mente e nosso corpo.</p>
       <p>Corpo. Foi uma caminhada marcada pela construção do entendimento de "corpo", na construção da autoconfiança. A confiança de nos entendermos dentro da nossa existência, como menina, adolescente e mulher. Confiança no que representamos por onde passamos, com quem convivemos e na história que escrevemos, um dia de cada vez. Ainda há muito que caminhar.</p>
       <p>A nossa história, de menina e mulher baiana, de Salvador, foi permeada, também, pela história da mamãe. E nós, sempre buscando a tal da felicidade. Mas antes de falar sobre a felicidade, quero falar do nosso corpo.</p>
       <p class="sem-indent">Corpo, um substantivo masculino… Masculino como olhar que nos colocou em uma posição precoce, ainda muito cedo.</p>
       <p>Embora eu enxergasse você como a criança que era, de 10 anos, os nossos seios chegavam antes, sexualizando um corpo que ainda era infantil e não entendia aquilo tudo. Lembra como aquelas situações geravam estranheza? A mamãe percebeu e nos protegeu, hoje eu entendo. Nos protegeu dos olhares do substantivo masculino.</p>
       <p>Você lembra quando foi que começamos a perceber isso? Na adolescência, quando nosso corpo passava na frente do R.G. Nunca pediram o nosso documento, lembra?</p>`,

      `<p>A mamãe orquestrou tudo, porque nós não tínhamos o olhar malicioso. Era o nosso corpo, simplesmente o nosso corpo. Esse corpo que abriga a nossa história. Nós não questionávamos suas partes, estava tudo bem pra nós, não é?</p>
       <p>Mas, a mamãe sabia que não estava! Agora, você segue junto comigo, hoje, com seios menores e mais mulher do que antes.</p>
       <p class="sem-indent">Lembro como foi passar por essa mudança. O corpo chegou na frente novamente, despertando questionamentos, curiosidades e a mudança no olhar de muitas pessoas.</p>
       <p>Nosso corpo se transformou e continua se transformando. Vou te contar. Nós engordamos 30 quilos, sério! E quer saber? Estamos ótimas! Aliás, peço desculpas pela distopia no olhar e por julgar nosso corpo quando ele só pesava 53 quilinhos. Era lindo! Continua lindo! Nós somos uma mulher, uma bela gostosa com 77 quilos na balança.</p>
       <p>Nós continuamos construindo um olhar amoroso sobre nós, como uma mulher inteira. Sabe, parte dessa construção é perceber, de maneira consciente, a mesma distopia em tantas mulheres que se olham, na tentativa de se enxergar.</p>
       <p>Talvez, por tudo isso, mesmo que no inconsciente, eu tenha resolvido me envolver com o estudo de gênero. Aliás, nos formamos em psicologia! Demais, não é?!</p>`,

      `<p class="sem-indent">O que nos move é o aprendizado de nos reconhecermos, nos amando ainda mais como somos, em qualquer tempo. Me percebo nos encontrando dentro da nossa história e dos diferentes corpos que já tivemos, e ainda vamos nos enxergar. Vamos nos compondo e nos complementando. Seguimos, juntas!</p>
       <p>A profissão que escolhemos faz parte de todo esse entendimento, porque escutar cada mulher complementa a mulher que somos e faz parte da busca da tal da felicidade.</p>
       <p>Aliás, sabe o que nos deixa feliz? Coisas simples, como pisar na areia da praia e colocar um biquini sem a preocupação do olhar das pessoas. Ouvir e fazer parte do autoconhecimento de mulheres, como nós, e lutar para que elas caminhem em segurança e que possam usar a roupa que quiserem, sem medo do julgamento.</p>
       <p>Somos felizes, Thainá, pela história que você ajudou a construir até aqui.</p>
       <p>Obrigada.</p>`
    ]
  },

  /* ========================================================================
     BLOCO 07 — CARTA V · Márcia
     ======================================================================== */
  {
    id: "marcia",
    numero: "V",
    nome: "Márcia",
    saudacao: "Marcia… Marcinha",
    idade: "54 anos",
    cidade: "Itaim Paulista",
    foto: "fotos/marcia.jpg",
    epigrafe: "As tramas que embalariam nosso fim, deram início ao recomeço.",
    assinatura: "Márcia",
    paginas: [
      `<p class="sem-indent">Marcia… Marcinha, olha onde nós estamos!</p>
       <p>Não só onde estamos hoje, mas, onde estamos na vida… As tramas que embalariam nosso fim, deram início ao recomeço. Foi ali que realmente nascemos.</p>
       <p>A memória dessa nossa história está na energia que depositamos na vontade de viver, porque os fatos foram narrados pelas vozes de quem nos embalou.</p>
       <p>Quanta bagagem trazemos nessa mala, embora a mortalha tenha ficado pra trás, impregnou com seu significado as linhas de outras vestes que tenho deixado pelo caminho, aos poucos. Faço isso por mim e por você. Você foi uma sobrevivente para que eu pudesse ser uma vivente. Teve gente que não acreditou que aquelas perninhas dariam os primeiros passos, muito menos que estaríamos aqui, hoje com 54 anos neste festival que leva o nome doce de MEL e que tem a força do vôo, de tantas que voam como nós — Mulheres em Lutas.</p>
       <p class="sem-indent">Você, Marcinha, caminhou bastante. Se soubesse de todo o percurso ainda pequena talvez tivesse se assustado. Mas, adianto que deu tudo certo. De uma gestação indesejada no Itaim Paulista para Pindamonhangaba. Da mortalha pra vida.</p>
       <p>Posso te dizer uma coisa? Você nunca atrapalhou o relacionamento dela… da Ana. Ela é que se atrapalhou pela vida e no meio de todo aquele caos, nos deu a vida de presente, pra tanta gente.</p>
       <p>Laços sanguíneos, de um vermelho frágil e com nós frouxos. Irmãos que perambulam pela vida enquanto construímos nossos próprios laços, firmes, que sustentam nossa base. Dorinha… Uma artesã pronta pra ser mãe de tantos corpos que estavam à espera da mortalha e ela… costurou a vida.</p>
       <div class="dialogo">— Oh Zé, a Ana tá dando uma criança, posso pegar? 1 ano e 8 meses.<br>— Tá! Se eu gostar ela fica, se não você leva ela embora.</div>`,

      `<p class="sem-indent">O primeiro som que a Dorinha ouviu da nossa boca foi um choro sentido, engasgado pela água que escorria, dos pés à cabeça, banhando como um fruto pendurado no pé num dia de chuva. Mesmo que a raiz nos mandasse calar, na agressividade de quem personifica o próprio rancor, insistimos pela vida.</p>
       <p>Superamos as feridas, do corpo e da alma, e, no lugar delas, plantamos amor. O mesmo amor que recebemos e que, talvez, demoramos a perceber de onde vinha. Vinha de todos os lados, da Dorinha e das vizinhas, entre chás, abraços e sorrisos. Até o Zé, que falou pra devolver porque a gente não ia sobreviver, viveu pra ver.</p>
       <p>Uma mulher rondava, querendo se aproximar, nos abraçava vez ou outra. Era estranho, nós tínhamos uns seis anos. A Dorinha fez tudo com muito amor e respeito, em doses homeopáticas. Esse abraço vinha da Ana.</p>
       <p>Não, ela nunca foi nossa mãe, Marcia. Mãe é maternar, símbolo de vida. Dorinha, ela sim é nossa mãe.</p>
       <p class="sem-indent">Precisamos falar de um período doloroso, mais um na verdade. Você só vai ter coragem de contar pra mamãe sobre o abuso que sofremos por tanto tempo já bem mais velha. Ficou muito tempo por dizer e eu fiz isso por nós, não tem tanto tempo.</p>`,

      `<p>Infelizmente você vai se calar, e se culpar, como tantas de nós fazemos. Ainda hoje eu repito pra mim mesma, pra que a gente se livre desse sentimento de culpa. Culpa que só pertence a esse senhor que compartilhou o teto com a nossa família como um favor que foi pago com a nossa pele, com o nosso corpo. Branco que se aproveitou da inocência de uma criança que tem essa memória desde, pelo menos, os cinco anos. Quantas de nós existem por aí, com essa mesma dor.</p>
       <p>Os ciclos e os ritos de passagem acontecem de acordo com cada história. A nossa foi de muitos desafios. Com frutos que embalamos com muito amor para sair da premissa de que só doamos o que recebemos. A rejeição que recebemos da Ana não determinou nossa relação com os filhos que tivemos. Foram três.</p>
       <p class="sem-indent">A arte nasceu junto com a gente, Marcia. Renascemos pelas mãos de uma artista, uma artesã humana, competente e corajosa. Precisou de muita coragem pra fazer da mortalha um abrigo.</p>
       <blockquote class="citacao">Tinha um bichinho que me corroía por dentro e eu não sabia o que era.</blockquote>
       <p>Já era a artista abrindo espaço pra nascer e florescer, para trazer cor em um terreno que estava cheio de erva daninha.</p>
       <p>Há 25 anos, fomos cheias de alegria para Pindamonhangaba, com o coração cheio de esperança e a proposta de construirmos uma vida melhor. Mas os blocos dessa construção eram de mentira, fomos enganadas e tiraram de nós o pouco dinheiro que havia. A vontade de viver… essa nunca conseguiram tirar. Somos sobreviventes!</p>
       <p>O pouco dinheiro que nos restou se transformou em um cavalo para nos guiar catando papelão. Vergonha… eu sentia muita vergonha e não sinto vergonha em admitir. Seguimos, com vergonha mesmo.</p>`,

      `<p class="sem-indent">A pior coisa é se enxergar à margem da sociedade. Estar à margem só nos permite dar passagem e assistir a vida passar. Nós nascemos para construir a própria história.</p>
       <p>A nossa sorte, se podemos chamar assim, é que a vontade de viver unida à consciência de que podíamos transformar aquela realidade nos fez enxergar poesia e conhecimento em meio ao papelão. Sempre que encontrava um livro no meio do papelão, parava pra ler.</p>
       <p>A arte nos salvou e me salva ainda hoje, a cada dia. Começamos a fazer teatro, com 42 anos. Conheci a história da Carolina Maria de Jesus, uma escritora com uma história muito parecida com a nossa.</p>
       <blockquote class="citacao">Nós não somos o papelão, nunca fomos. Aquele era só um momento.</blockquote>
       <p class="sem-indent">Em 2024 eu saí candidata a vereadora pelo PSOL e ganhei a minha vida de volta. Revisitei esses lugares todos da minha vida por conta da minha candidatura e isso tem me curado.</p>
       <p>Trazer a experiência do abuso pode servir de referência para outras crianças que vivem essa mesma realidade. Quero contar essa história cada vez mais. A nossa história pode encorajá-las a falar.</p>
       <p>Eu levo a história da Carolina, pelo monólogo, há muitas outras mulheres, inclusive em presídios femininos. A mensagem é simples… Não deixe que nada mate seus sonhos.</p>
       <blockquote class="citacao">Todo dia eu abro a janela do barraco e penso. Quem sabe do outro lado da vida tem algo melhor.<span class="citacao-atribuicao">— Carolina Maria de Jesus</span></blockquote>
       <p class="sem-indent">Eu me identifiquei, mas nunca tive coragem por causa dos meus filhos. Tinha uma linha de trem atrás do meu barraco e eu pensava em me jogar ali, no momento certo. Fazia isso chorando, até que minha filha enxugava minhas lágrimas e me fazia desistir.</p>`,

      `<p>Entendo o poder que a nossa história tem e entendo que, em meio a tantas histórias diferentes, há tantos sentimentos iguais, que convergem e que lutam para se manter dentro de cada uma de nós. Até que em algum momento nos damos conta e nos livramos de todos eles: da culpa, do sentimento de abandono, do não merecimento, do não pertencimento.</p>
       <p>Por isso, eu digo mais uma vez: Pode seguir, venha com a calma. Você construiu uma história linda em meio ao caos e eu estou aqui para dar continuidade porquê ainda há muito para viver!</p>
       <p>Com amor,</p>`
    ]
  },

  /* ========================================================================
     BLOCO 08 — CARTA VI · Hosana
     ======================================================================== */
  {
    id: "hosana",
    numero: "VI",
    nome: "Hosana",
    saudacao: "Oi, Hosana",
    idade: "",
    cidade: "Mauá · SP",
    foto: "fotos/hosana.jpg",
    epigrafe: "Desisti de desistir.",
    assinatura: "Hosana",
    paginas: [
      `<p class="sem-indent">Eu poderia cantar a nossa história, com uma melodia completa, dançando entre dramas, potências e conquistas.</p>
       <p>Embora tantos desafios, nossa vida é uma música harmônica, cheia de rimas, ritmo e vibração.</p>
       <p>Quando decidimos, aos 11 anos trocar a Igreja pela quadra da escola de samba, ainda não imaginávamos o que vinha pela frente. Respira fundo, vou te contar.</p>
       <p>Você não imagina a potência de mulher e ser humano no qual nos transformamos, Hosana. A maternidade nos forjou, ainda quando éramos apenas uma criança de 14 anos. Jaque, é o nome da nossa primeira filha, hoje com 31 anos.</p>
       <p>Somos fruto do que você foi construindo ao longo da vida, com as decisões e personalidade fortes que trilharam o caminho até aqui. Obrigada pela sua coragem.</p>
       <p class="sem-indent">Quando nossos pais chegaram em Mauá em 64, atravessando o mapa em meio a uma ditadura, começaram a marcar uma caminhada que quebraria padrões e ciclos de estereótipos impostos involuntariamente. A Bahia e o Pernambuco fazendo parte da construção da metrópole que serve de palco para desconstruir.</p>
       <p>Lembra, ainda pequena, nossa mãe se dividindo entre sete filhos? Penso com carinho da espera do momento em que o papai chegava do trabalho e ia preparar o que eu — você — queria comer. Embrutecido pelo sofrimento do sertão do nordeste, ele guardava espaço para cuidar. Foi a base dessa cultura de cuidado que permeia nossa trajetória.</p>`,

      `<p>Somos mãe. Quatro pessoas humanas às quais dedicamos toda energia, servindo de espelho para que criassem reflexos diferentes dos que recebemos. Negros, periféricos criando a própria realidade, repudiando imposições sociais de manutenção da pobreza e da ignorância.</p>
       <p>Sabe do melhor? O Pedro. Nós escolhemos o Pedro, junto com nossos filhos, e também fomos escolhidas por ele. Temos uma família linda, potente, que já deu continuidade à linhagem, com um netinho de um ano e meio.</p>
       <p class="sem-indent">Com a Jaque, quebramos o ciclo de gravidez na adolescência. Criamos e educamos uma mulher que trilha o próprio caminho. Negra, periférica, sem filhos e na universidade, com 31 anos. Vem tranquila, você fez um bom trabalho.</p>
       <p>Existe algo em nós muito genuíno. Embora a cultura evangélica permeasse nossa infância e educação, a compaixão não foi suficiente para que nos acolhesse enquanto esperávamos a Jaque nascer. Fomos culpabilizadas e responsabilizadas por não termos o esclarecimento que deveríamos ter recebido. A culpa não foi sua, não é nossa.</p>
       <p>Se prepara, Hosana, vai ser dolorido. Mas vai valer a pena. A maternidade vai te forjar e vai te impulsionar, junto com a Cultura e a Arte que estão na sua alma. Tudo isso vai te dar pulsão de vida.</p>`,

      `<p>O samba, o estudo e o rap fizeram parte da construção da nossa personalidade. Trabalhamos a nossa autoestima e nunca tivemos vergonha da ancestralidade, da cultura africana e da nossa negritude. A música é uma ferramenta de conexão com o divino que há dentro de nós.</p>
       <p class="sem-indent">Só voltamos a estudar com 34 anos, mais ou menos. Viu, nunca é tarde. EJA — Educação de Jovens e Adultos. Foi lá que terminamos os estudos. Nós gostamos de estudar!!!</p>
       <p>Fomos corajosas, mesmo sem o apoio da família. Nos formamos em Ciências Sociais. Levar para o trabalho o que sempre nos moveu na vida. Cuidar.</p>
       <p>A primeira coisa mais importante que fizemos, e você me deu coragem pra isso, foi o divórcio. A segunda, foi Deitar pro Santo. O candomblé orienta nossa vida. A africanidade nos dá poder!</p>
       <p>Quando entramos na faculdade ao mesmo tempo que entramos para o movimento negro de esquerda, tiramos o peso da ignorância e pegamos o peso da responsabilidade de entender e escolher o que fazer com o conhecimento. A resposta foi o engajamento político, não paramos mais de militar.</p>
       <p>Entrei para o PSOL. A política é necessária, mas também é difícil, tentam nos silenciar a todo momento. Embora não tenha sido eleita, fomos a mais bem votada.</p>`,

      `<p class="sem-indent">Fui aprender a cuidar de mim quando me vi morando sozinha… e isso foi só há três anos, quando nossa filha resolveu cuidar dela mesma e saiu de casa. Eu pensei: Por que agora? Vou ter que cuidar de mim! Tem sido maravilhoso, puro autoconhecimento.</p>
       <p>Toda nossa base artística, do samba, do black, do rap, a arte negra e africanidade, exalaram pela nossa pele. Planto dessa semente com as crianças do CRAS, como monitora, trabalhando a arte e a música. Sigo fazendo a nossa parte, aprendi a cuidar dos outros sem deixar de cuidar de nós.</p>
       <blockquote class="citacao">Nós quase desistimos, sabia? Houve um tempo sem esperança e quase interrompi nossa trajetória. Mas siga firma porque desisti de desistir.</blockquote>
       <p>Agora, viver me movimenta como num palco com a nossa música preferida. A nossa música é pra todas e nosso palco é grande, cabe todo mundo.</p>
       <blockquote class="citacao">Somos diversas, mas não estamos dispersas. Vamos conseguir!<span class="citacao-atribuicao">— Marielle Franco</span></blockquote>
       <p>Obrigada pela base que nos sustenta, Hosana! Pode vir, estamos bem e seguimos sambando!</p>`
    ]
  },

  /* ========================================================================
     BLOCO 09 — CARTA VII · Marília Martins
     ======================================================================== */
  {
    id: "marilia",
    numero: "VII",
    nome: "Marília Martins",
    saudacao: "Oi, Marília",
    idade: "37 anos",
    cidade: "Franca · SP",
    foto: "fotos/marilia_martins.jpg",
    epigrafe: "Atrás de uma grande mulher tem sempre outra grande mulher.",
    assinatura: "Marília",
    paginas: [
      `<p class="sem-indent">Nossa, respira fundo. Tem muita coisa pra contar, Ma ou Marília… Faz tanto tempo… São 37 anos de história de páginas escritas por você, na evolução das letrinhas que hoje transmitem a segurança que sempre tivemos nos passos.</p>
       <p>Passos legítimos de pai e mãe, sapateiros, costurando o nosso caminho, caminho que nos trouxe até aqui, hoje. Somos a união de todas as emoções, conquistas e, preciso admitir, privilégios que acumulamos ao longo de todos esses anos.</p>
       <p>A vontade de ser livre na nossa essência nos transformou em uma mulher que trabalha com o compromisso de garantir essa liberdade para todas as mulheres que pudermos alcançar.</p>
       <p>Somos circulares, assim como a dança que permeia nossa existência. Fazemos parte de uma transformação genuína e orgânica com raízes que fortalecem a nossa luta, até hoje. Determinação que vem da nossa ancestralidade. A vovó criou sete filhos, viúva, você lembra, né? A menina sapateira de 08 anos se formou professora. O papai, advogado.</p>
       <p class="sem-indent">Entre letras, eventos e sala de aula, hoje estamos na política. Somos vereadora em Franca pelo PSOL, partido que ajudamos a fundar na cidade, em 2007, 2008. Aposto que você já sabia, afinal crescemos no movimento sindical e no MST.</p>`,

      `<p>Mas, antes disso, dançamos em lugares diferentes e voamos pra longe. Sabe o tal do privilégio? Então… nos formamos em Planejamento de Eventos Conscientes nos Estados Unidos. Temos uma bagagem rica de planejamento e políticas públicas para servir, agora, tantas mulheres que precisam de rede de apoio.</p>
       <p>Esses momentos me fazem lembrar das 17 vezes que o papai foi cassado e processado pela ditadura militar, na tentativa de promover justiça social. Seguimos os mesmos passos: Educação e política. Dalvinha e Georginho.</p>
       <p>Também somos professoras. Até criamos uma cartilha: <em>"Vira a Página, Mulher"</em>. Viramos, cada página lida.</p>
       <p class="sem-indent">Nossa vida política se fortaleceu quando voltamos dos EUA, cansadas da cultura essencialmente capitalista. Com um cachorrinho embaixo dos braços, alugamos uma casa que se transformou em um coletivo de mulheres.</p>
       <p>Nossa casa ganhou até nome: Confraria Cult. Tantas coisas boas acontecem por lá… meditação, roda de conversas, danças circulares, eventos de humanização e políticas públicas para mulheres e até feiras de mulheres artesãs para promover independência e autonomia financeira. Nossas mulheres artesãs, hoje, até exportam seus materiais. É um projeto lindo, que nasceu antes mesmo de estarmos vereadora.</p>`,

      `<p>Aliás, sempre me recolho, faço meditação e às vezes encontro com você, ainda quando éramos uma menina. Ah, gostamos de menina, e namoro uma mulher incrível que é o nosso grande apoio. Consegue imaginar assumirmos isso aqui em Franca? Pois é, tudo isso faz parte da nossa luta, Marília.</p>
       <blockquote class="citacao">Atrás de uma grande mulher tem sempre outra grande mulher!</blockquote>
       <p>Cada plantinha que eu cultivo também estou regando os nossos sonhos e humanizando uma luta que às vezes é dolorida e densa. Precisamos equilibrar o nosso ser, que é holístico.</p>
       <p>Nossa vida política tem seus riscos e passamos alguns apuros que pegaram fogo, literalmente. Mas, temos vizinhos bacanas e uma rede de apoio imensa que ajudaram a apagar. As autoridades tentam nos desencorajar e, mesmo recuando em alguns momentos, seguimos em frente, menina.</p>
       <p>Nossa luta significa encontrar pessoas dispostas a conversar para a solução de problemas, não só pelo desabafo. Teremos alguns anos pela frente com a nossa voz em volume máximo, <em>"depois, eu ajusto as velas e reavalio"</em>.</p>
       <p>Obrigada por tudo o que você fez até aqui. Agora, deixa comigo. Vou fazer um bom trabalho!</p>
       <p>Sinta meu abraço, apertado, e um beijo na bochecha.</p>`
    ]
  },

  /* ========================================================================
     BLOCO 10 — CARTA VIII · Ariane
     ======================================================================== */
  {
    id: "ariane",
    numero: "VIII",
    nome: "Ariane",
    saudacao: "Ariane… Ariane pequena",
    idade: "",
    cidade: "",
    foto: "fotos/ariane.jpg",
    epigrafe: "Acabou o gás… mas não acabou a comida.",
    assinatura: "Ariane",
    paginas: [
      `<p class="sem-indent">Eu queria poder sentar ao seu lado naquele chão de terra, onde você ainda não sabe, mas já aprendeu tudo.</p>
       <p>Queria te observar de longe, antes de você perceber o peso que o mundo tenta colocar nas suas costas. Antes de você acreditar, por um segundo que seja, que não é suficiente.</p>
       <p>Você vai se descobrir mulher, uma mulher inteira sem que ninguém te diga o que pode ou não pode fazer, porque você é exclusivamente dona e responsável pela sua própria vida. Vão tentar te dizer o contrário, mas rapidamente você vai enxergar com clareza, pode ficar tranquila, menina.</p>
       <p>Você ainda não sabe, mas naquele dia em que o gás acabou… não foi só comida que você fez. Você acendeu uma mulher na origem da chama de outra, do cansaço de outra, das lágrimas de outra.</p>
       <p>Você pegou tijolo, graveto, fogo… o que você podia, e fez nascer em você uma força que nunca mais te abandona. Por causa dessa força você vai ouvir seu nome quando tudo desmoronar: <em>"Deixa com a Ariane."</em> E você vai deixar. Vai resolver. Vai aguentar. Vai ir até o fim… mesmo quando estiver cansada demais.</p>
       <p>Mas escuta uma coisa importante, que ainda vai levar tempo pra você entender: você não precisa dar conta de tudo sozinha o tempo inteiro. Nem toda força precisa ser solitária.</p>
       <p class="sem-indent">Você vai crescer rápido demais. Vai ser irmã mais velha antes de ser só filha. Vai ser mãe antes de entender o que isso significa. E sobre isso… eu preciso te contar com cuidado:</p>`,

      `<p>Você vai amar sua filha, a nossa filha, a nossa Maria Eduarda… Vai amar de um jeito que não cabe no corpo. Um amor bruto, visceral, que dá vontade de proteger o mundo inteiro com as mãos.</p>
       <p>Mas também vai sentir medo. Cansaço. Dúvida. E tudo bem! Você vai encontrar muita gente romantizando a gravidez e a maternidade e vai sentir na própria pele que não é assim. Sinta isso sem culpa, somos uma mãe maravilhosa!</p>
       <p>Porque você nunca foi só mãe. Você sempre foi mulher antes disso. E sabe o que é mais bonito? Você vai ensinar isso pra ela.</p>
       <p>Vai ensinar que mulher pode sair, dançar, rir alto, escolher. Que liberdade não é erro. Que existir da maneira que se quer não é motivo para se desculpar. E, Ariane… Ela vai te enxergar, com amor e respeito.</p>
       <p>E nesse dia, você vai entender que fez tudo certo, mesmo achando que não. Ela vai te enxergar como mulher, antes da mãe.</p>
       <p class="sem-indent">Agora deixa eu te contar uma coisa que talvez doa um pouco: você vai se olhar no espelho por muito tempo… e não vai gostar do que vê. Vai achar que seu corpo é errado. Que você não é bonita. Que não cabe.</p>
       <p>E isso não nasceu em você. Essa angústia e essa sensação de que existe um jeito certo de ser bonita foi implantada na sua cabeça, assim como é feito com todas as mulheres. Não há corpo certo e errado. Cada uma de nós carrega a beleza de ser quem realmente somos.</p>`,

      `<p>Mas, um dia… um dia você vai se olhar diferente. Vai vestir uma roupa e não pedir permissão. Vai mostrar a pele sem vergonha. Vai rir do que antes te travava. E quando alguém tentar te diminuir… você já não vai caber mais nesse lugar.</p>
       <blockquote class="citacao">Meu corpo é meu.</blockquote>
       <p class="sem-indent">Você também vai conhecer o amor… mas não aquele que prende, diminui, ameaça. Você já conheceu esse. O que chega depois é outro. Um amor que não te corta. Que não te apaga. Que te deixa ser. Um amor que olha pra você e diz, sem medo: <em>"Vai. Viva. Seja quem você é."</em></p>
       <p class="sem-indent">Agora, me escuta com atenção: você é uma mulher preta. Forte. Barulhenta. Viva. E vão tentar te silenciar.</p>
       <p>Vão tentar te fazer menor. Menos bonita. Menos capaz. Menos tudo. Mas você não é menos. Você é muito. Muito de tudo. E é exatamente isso que incomoda.</p>
       <p>Então não se diminua. Não abaixe sua cabeça. Não pede desculpa por existir do seu jeito. Você vai trazer na sua essência de mulher a mesma <em>"maluquinha"</em> de sempre, e isso é maravilhoso. Talvez seja só livre demais pra um mundo que ainda não sabe lidar com isso.</p>
       <p>E, Ariane… guarda esse sonho que você nem sabe ainda o tamanho que tem: você vai querer ensinar. Vai querer mostrar pra outras pessoas, especialmente aquelas que acham que já passou o tempo, que dá, que é possível.</p>`,

      `<p>Vai mostrar que sempre dá. Que estudar depois, voltar, tentar de novo… também é vitória. Você vai querer falar sobre cultura, sobre história, sobre quem você é. Sobre a importância e o valor da cor da nossa pele! Somos lindas! E quando você fizer isso… você não vai estar apenas ensinando. Você vai reparar o mundo.</p>
       <p>E por fim… se em algum momento você esquecer quem você é… lembre da menina de 12 anos, com o rosto sujo de fumaça, orgulhosa diante de um fogão improvisado, dizendo:</p>
       <blockquote class="citacao">Acabou o gás… mas não acabou a comida.</blockquote>
       <p class="sem-indent">Ali… ali nasceu tudo. E continua nascendo. Continue crescendo, vivendo!</p>
       <p>Com amor,</p>`
    ]
  },

  /* ========================================================================
     BLOCO 11 — CARTA IX · Paula
     ======================================================================== */
  {
    id: "paula",
    numero: "IX",
    nome: "Paula",
    saudacao: "Paula… Paulinha, vem cá",
    idade: "",
    cidade: "",
    foto: "fotos/paula.jpg",
    epigrafe: "Aquela menina nunca precisou ser consertada. Ela só precisava ser compreendida.",
    assinatura: "Paula",
    paginas: [
      `<p class="sem-indent">Eu sei que você ainda não entende muita coisa. Mas você sente. E sentir… sempre foi o seu primeiro idioma.</p>
       <p>Você observa mais do que fala. Percebe o que ninguém nomeia, porque não precisa de rótulos. Feminismo e toda essa militância que faz parte da nossa essência, foi aprendida de maneira empírica.</p>
       <p>E, mesmo sem saber explicar, já existe em você uma inquietação que não cabe dentro da infância. Você acha que é exagero, mas não é. É lucidez nascendo cedo demais.</p>
       <p>Você cresceu num lugar onde o amor não era dito, era feito. Como bem diz bell hooks: <em>amar é verbo, é ação</em>. E eu sei que isso, às vezes, confunde, porque você aprende a ler o cuidado nas entrelinhas, mas cresce sem saber exatamente como pedir colo.</p>
       <p>A presença feminina, latente, no nosso dia a dia, foi decisiva para nos tornarmos quem somos hoje. Você morreria de tanto orgulho. Essa essência vem da mamãe, que sempre ocupou o espaço que lhe cabia quando ainda nem se falava disso. Fomos educadas por uma mulher que não sabia o nome do feminismo, mas sabia vivê-lo. E isso… isso te atravessou inteira.</p>
       <p class="sem-indent">Vai chegar um momento em que você vai querer entender o mundo. E você vai estudar… ao redor do mundo. Vai unir a teoria com a experiência e isso vai enriquecer a vida de quem estiver perto de você, muito. Vai mergulhar em histórias, teorias, nomes que hoje você nem imagina.</p>
       <p>E aí… Paulinha… vai doer. Porque conhecer é sinônimo de perder um tipo de inocência que nunca mais volta. Você vai perceber que aquilo que parecia individual… nunca foi só seu.</p>`,

      `<blockquote class="citacao">Toda vez que a gente come o fruto do conhecimento, a gente é expulsa de um paraíso.<span class="citacao-atribuicao">— Melanie Klein</span></blockquote>
       <p class="sem-indent">E eu senti que eu não fui expulsa — eu fui chutada e fui rolando, porque não tem volta, não tem como desver nada, não tem como desconhecer o que já é conhecido.</p>
       <p>E quando você entender isso… não tem retorno. Mas deixa eu te contar: essa dor não te destrói. Ela te posiciona. Você vai se tornar uma mulher que escuta. E escuta de verdade.</p>
       <p>Vai carregar histórias de outras mulheres como quem segura algo sagrado. Vai perceber padrões, repetições, feridas que atravessam corpos diferentes. E vai se fazer uma pergunta que muda tudo: <em>"como pode ser coincidência?"</em> Não é.</p>
       <p class="sem-indent">Paula, eu preciso te preparar para algumas coisas que você não deveria viver… mas vai. Nem todo espaço é seguro. Nem todo gesto é cuidado. E vai ter momentos em que o seu corpo vai saber antes da sua consciência.</p>
       <p>Você vai tentar entender. Vai buscar lógica onde só existe violência. Eu queria tanto poder te poupar disso… mas eu não posso. O que eu posso é te dizer:</p>
       <blockquote class="citacao">Você não foi responsável.<br>Você não provocou.<br>Você não escolheu.<br>Você não mereceu.</blockquote>
       <p class="sem-indent">E mesmo quando você não lembrar… o seu corpo vai lembrar por você. Vai levar tempo até você conseguir nomear isso. Vai levar tempo até você parar de se perguntar <em>"por quê"</em>. Mas um dia… você vai parar de se culpar. E esse dia muda tudo.</p>
       <p>Você vai continuar, mesmo com medo. Mesmo com raiva. Mesmo com essa sensação de que o mundo é maior, e mais injusto, do que você imaginava.</p>`,

      `<p>E sabe o que é mais bonito nisso tudo? Você não vai endurecer. Você vai ficar mais afiada, mais crítica, e combativa… mas também vai aprender, aos poucos, a ser afetiva. Vai ser um exercício, quase diário. Porque falar firme sempre foi mais fácil do que falar com doçura. Se posicionar sempre foi mais natural do que se abrir.</p>
       <p class="sem-indent">Você vai amar cuidando — essa é a sua linguagem: o cuidado. Vai amar dizendo. Vai amar tentando. O mais importante: você vai se autorizar a viver tudo o que tiver vontade sem se forçar a permanecer em lugar algum ou em nenhum relacionamento.</p>
       <p>E, aos poucos… vai se permitir sentir. Inclusive prazer, especialmente a liberdade, especialmente <em>com</em> liberdade. Um dia você vai olhar pra sua sexualidade sem medo. Sem culpa. Sem precisar caber em nenhuma regra que não faça sentido pra você.</p>
       <p>Estudar se tornou uma missão. Com 17 anos você vai estar na faculdade: psicologia. Entender a mente humana é uma baita responsabilidade! E isso… isso também é revolução.</p>
       <p>Você ainda não sabe, mas existe uma palavra que vai te acompanhar pela vida inteira: <em>justiça</em>. Ela já mora em você e assim nós somos: justiceiras. Continuamos inconformadas com injustiça e isso é a base do trabalho de escuta que fazemos há mais de 21 anos. Nosso trabalho é lindo, e necessário.</p>
       <p>Você vai acordar com vontade de mostrar para outras mulheres que elas não estão erradas. Que existe uma lógica maior, coletiva, estrutural. Que a dor delas faz sentido. Elas entenderão que não estão sozinhas, que há muitas como elas, como eu, como você. Você vai devolver voz para quem foi silenciada.</p>`,

      `<blockquote class="citacao">Aquela menina nunca precisou ser consertada. Ela só precisava ser compreendida.</blockquote>
       <p class="sem-indent">Então vem tranquila. Não precisa correr. Você não precisa dar conta de tudo agora. A vida vai te atravessar, sim. Mas você também vai atravessar a vida, com consciência, com coragem e com uma força que você ainda nem imagina que tem.</p>
       <p>Você vai ficar orgulhosa da mulher que se tornou e que, no fundo, sempre esteve aí, dentro de você.</p>`
    ]
  },

  /* ========================================================================
     BLOCO 12 — CARTA X · Sheila
     ======================================================================== */
  {
    id: "sheila",
    numero: "X",
    nome: "Sheila",
    saudacao: "Oi, Sheilinha",
    idade: "quase 70 anos",
    cidade: "",
    foto: "fotos/sheila.jpg",
    epigrafe: "Você também é… uma travessia, VIVA.",
    assinatura: "Sheila",
    paginas: [
      `<p class="sem-indent">Há quanto tempo a gente não se encontra assim, né? Eu queria ter vindo mais vezes, ter sentado ao seu lado em outros momentos… mas talvez a vida tenha o tempo certo das coisas. E agora, aos quase 70 anos, eu sinto que esse encontro precisava acontecer.</p>
       <p>Setenta anos… olha quanta vida cabe dentro disso. Você ainda nem imagina, mas vai viver muito. Intensamente. Do seu jeito. E eu não vou te enganar: não vai ser fácil.</p>
       <p>Vão existir muitas pedras no caminho, algumas tão grandes que você vai achar que não vai conseguir atravessar. Mas tem uma coisa que eu preciso te contar logo de cara — e talvez seja a mais importante de todas:</p>
       <blockquote class="citacao">Você nunca vai perder a sua alegria.</blockquote>
       <p class="sem-indent">Esse seu jeito leve, de rir alto, de brincar na rua como se o mundo fosse inteiro seu… isso fica. Mesmo quando a vida apertar, mesmo quando o peito doer, mesmo quando a bronquite vier e você continuar ali, com o nariz sujo, o corpo cansado e o coração inteiro. Essa menina não vai embora.</p>
       <p>Você vai duvidar de si muitas vezes. Vai se sentir pequena, vai se sentir deixada de lado, vai tentar entender por que, tantas vezes, parece que você está amando mais do que sendo amada. Mas, ao mesmo tempo, vão ter momentos em que você vai perceber: as pessoas te procuram. Elas gostam de te ouvir, gostam da sua presença, da sua energia, do seu jeito de estar no mundo. Isso também é amor.</p>
       <p class="sem-indent">Nossa infância teve cor, teve rua, teve liberdade. Você queria tudo que via pela frente — até ferro velho virava desejo. Andou de bicicleta, caiu, levantou, riu… nunca teve muito medo de tentar. E isso diz muito sobre quem você é.</p>
       <p>Você nasceu em um tempo em que ser mulher já vinha com um roteiro pronto. E, de alguma forma, você seguiu esse roteiro… casou, teve filhos, construiu uma família. Mas nunca coube completamente dentro dele.</p>`,

      `<p>Você sempre foi grande demais pra caber em qualquer lugar que tentassem te colocar. Por isso, eu escolhi seguir alguns caminhos que foram mais solitários. Não tenha medo, porque valeu a pena. Porque isso permitiu que você, que nós, criássemos nossos próprios espaços, sem precisarmos nos apertar.</p>
       <p class="sem-indent">Teve um lugar… que talvez tenha sido um dos poucos em que você se sentiu inteira. <em>O Travessia</em>.</p>
       <p>Não era só uma choperia. Era um pedaço de nós existindo no mundo. Tinha música, tinha encontro, tinha gente, tinha vida acontecendo. Tinha aquele som que atravessava a noite e parecia dizer, baixinho, que apesar de tudo… havia beleza.</p>
       <p>Ali, você foi feliz. E você sabe disso. Talvez por isso doa tanto lembrar. Porque perder o Travessia não foi só perder um negócio. Foi perder um lugar onde você se reconhecia, onde a vida fazia sentido, onde você não era <em>"a que faltava"</em>, mas a que transbordava.</p>
       <p>E mesmo assim… você seguiu. Tudo fez parte das nossas escolhas. Virar a página também é uma escolha.</p>
       <p>Tiveram perdas que chegaram sem pedir licença. Coisas que escaparam das suas mãos antes mesmo de você conseguir entender. Planos que não se sustentaram, caminhos que não deram certo. E teve também aqueles períodos em que a vida pareceu fechar as portas — literalmente e por dentro.</p>
       <p>Mas, ainda assim, você ficou. Você sustentou e precisou segurar em grades que trancafiavam uma parte de você, por algum tempo… você não virou as costas para o amor. E isso diz mais sobre você do que qualquer dor que tenha atravessado.</p>
       <p class="sem-indent">Você é intensa, Sheilinha. Sempre foi. Ama muito, se entrega muito, espera muito… e quando não encontra do outro lado o que imaginou, se machuca, se fecha, tenta se proteger como pode. Às vezes com julgamento. Às vezes com silêncio. Às vezes guardando aquilo que não conseguiu dizer.</p>`,

      `<p>Mas olha que coisa bonita — mesmo assim, você nunca deixou de amar. Nunca deixou de rir. Nunca deixou de ser transparente. Nunca deixou de ser você. E isso sustenta muita coisa.</p>
       <p>Você construiu uma relação linda com seus filhos. Uma relação de verdade, sem máscara, sem distância. Eles te conhecem, te enxergam, te amam — e isso não acontece por acaso. Isso é construção sua.</p>
       <p>Você também buscou sentido. Foi atrás da espiritualidade, tentou entender a vida para além do que te aconteceu. E hoje consegue olhar pra mamãe com mais compreensão… entende que ela também fez o que pôde, dentro do que aprendeu, dentro do que viveu.</p>
       <p class="sem-indent">Mas eu sei… tem uma parte sua que ainda mora lá atrás. Na volta de Belo Horizonte. Na sensação de que poderia ter sido diferente. No <em>"e se…"</em> que nunca termina.</p>
       <p>Talvez pudesse… mas talvez não. Porque, no fim, você fez escolhas com o coração que tinha naquele momento. Com as dores, com as faltas, com os desejos e com as limitações daquele tempo. E isso precisa começar a bastar, sem culpa e com amor pela nossa trajetória, que é linda!</p>
       <p>Você não precisa reescrever a sua história pra validar a sua vida. Ela já aconteceu. E ela tem valor — inteira, do jeito que é.</p>
       <p>Agora, aos quase 70, eu quero te convidar pra um outro lugar. Um lugar onde você não é mais a que mais sofreu… mas a que atravessou. A que caiu e levantou. A que perdeu e tentou de novo. A que amou — mesmo quando doeu. A que criou espaços de vida, como o Travessia… e também aprendeu a existir quando esses espaços já não estavam mais lá.</p>
       <p>A sua história não é leve. Mas ela é viva.</p>
       <blockquote class="citacao">E você também é… uma travessia, VIVA.</blockquote>
       <p class="sem-indent">Nem sempre do jeito que a gente planeja, nem sempre com a música que a gente escolheria, mas ainda assim… um caminho que segue. E olha só… você atravessou.</p>`,

      `<p>O Travessia nunca acabou, Sheilinha. Na verdade você nunca perdeu. Porque tudo isso vive, junto com a gente, nas nossas memórias de amor por tudo o que fizemos, por cada passo. Ela só deixou de ser um lugar… pra virar quem você é, quem eu sou, quem nós somos.</p>
       <p>Obrigada por tudo, até aqui. Agora eu continuo, com a mesma alegria. Prometo!</p>`
    ]
  },

];

/* ==========================================================================
   BLOCO 13 — EXPORT
   ========================================================================== */
if (typeof module !== 'undefined') module.exports = CARTAS;

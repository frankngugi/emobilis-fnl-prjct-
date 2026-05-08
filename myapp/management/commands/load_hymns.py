from django.core.management.base import BaseCommand
from myapp.models import Hymn


HYMNS_DATA = [
    # ═══════════════ ENGLISH HYMNS ═══════════════
    (1, "Holy, Holy, Holy", "Reginald Heber", "English",
     "Holy, holy, holy! Lord God Almighty!\nEarly in the morning our song shall rise to Thee;\nHoly, holy, holy! Merciful and mighty!\nGod in three Persons, blessed Trinity!\n\nHoly, holy, holy! All the saints adore Thee,\nCasting down their golden crowns around the glassy sea;\nCherubim and seraphim falling down before Thee,\nWho wert, and art, and evermore shalt be.\n\nHoly, holy, holy! Though the darkness hide Thee,\nThough the eye of sinful man Thy glory may not see;\nOnly Thou art holy; there is none beside Thee,\nPerfect in pow'r, in love, and purity.\n\nHoly, holy, holy! Lord God Almighty!\nAll Thy works shall praise Thy name in earth, and sky, and sea;\nHoly, holy, holy! Merciful and mighty!\nGod in three Persons, blessed Trinity!", "Praise"),

    (2, "Amazing Grace", "John Newton", "English",
     "Amazing grace! How sweet the sound\nThat saved a wretch like me!\nI once was lost, but now am found;\nWas blind, but now I see.\n\n'Twas grace that taught my heart to fear,\nAnd grace my fears relieved;\nHow precious did that grace appear\nThe hour I first believed.\n\nThrough many dangers, toils and snares,\nI have already come;\n'Tis grace hath brought me safe thus far,\nAnd grace will lead me home.\n\nThe Lord has promised good to me,\nHis Word my hope secures;\nHe will my Shield and Portion be,\nAs long as life endures.\n\nWhen we've been there ten thousand years,\nBright shining as the sun,\nWe've no less days to sing God's praise\nThan when we'd first begun.", "Grace"),

    (3, "How Great Thou Art", "Carl Boberg", "English",
     "O Lord my God! When I in awesome wonder\nConsider all the worlds Thy hands have made,\nI see the stars, I hear the rolling thunder,\nThy pow'r throughout the universe displayed.\n\nChorus:\nThen sings my soul, my Saviour God, to Thee:\nHow great Thou art! How great Thou art!\nThen sings my soul, my Saviour God, to Thee:\nHow great Thou art! How great Thou art!\n\nWhen through the woods and forest glades I wander\nAnd hear the birds sing sweetly in the trees;\nWhen I look down from lofty mountain grandeur\nAnd hear the brook and feel the gentle breeze.\n\nAnd when I think that God, His Son not sparing,\nSent Him to die, I scarce can take it in;\nThat on the cross, my burden gladly bearing,\nHe bled and died to take away my sin.\n\nWhen Christ shall come with shout of acclamation\nAnd take me home, what joy shall fill my heart!\nThen I shall bow in humble adoration\nAnd there proclaim, my God, how great Thou art!", "Praise"),

    (4, "Great Is Thy Faithfulness", "Thomas O. Chisholm", "English",
     "Great is Thy faithfulness, O God my Father;\nThere is no shadow of turning with Thee;\nThou changest not, Thy compassions, they fail not;\nAs Thou hast been, Thou forever will be.\n\nChorus:\nGreat is Thy faithfulness! Great is Thy faithfulness!\nMorning by morning new mercies I see.\nAll I have needed Thy hand hath provided;\nGreat is Thy faithfulness, Lord, unto me!\n\nSummer and winter and springtime and harvest,\nSun, moon and stars in their courses above\nJoin with all nature in manifold witness\nTo Thy great faithfulness, mercy and love.\n\nPardon for sin and a peace that endureth,\nThine own dear presence to cheer and to guide,\nStrength for today and bright hope for tomorrow —\nBlessings all mine, with ten thousand beside!", "Faithfulness"),

    (5, "What a Friend We Have in Jesus", "Joseph M. Scriven", "English",
     "What a friend we have in Jesus,\nAll our sins and griefs to bear!\nWhat a privilege to carry\nEverything to God in prayer!\nOh, what peace we often forfeit,\nOh, what needless pain we bear,\nAll because we do not carry\nEverything to God in prayer!\n\nHave we trials and temptations?\nIs there trouble anywhere?\nWe should never be discouraged;\nTake it to the Lord in prayer!\nCan we find a friend so faithful,\nWho will all our sorrows share?\nJesus knows our every weakness;\nTake it to the Lord in prayer!\n\nAre we weak and heavy-laden,\nCumbered with a load of care?\nPrecious Savior, still our refuge —\nTake it to the Lord in prayer!\nDo thy friends despise, forsake thee?\nTake it to the Lord in prayer!\nIn His arms He'll take and shield thee;\nThou wilt find a solace there.", "Prayer"),

    (6, "To God Be the Glory", "Fanny Crosby", "English",
     "To God be the glory, great things He hath taught us,\nGreat things He hath done, and great our rejoicing\nThrough Jesus the Son;\nBut purer and higher and greater will be\nOur wonder, our transport, when Jesus we see.\n\nChorus:\nPraise the Lord! Praise the Lord!\nLet the earth hear His voice!\nPraise the Lord! Praise the Lord!\nLet the people rejoice!\nO come to the Father through Jesus the Son,\nAnd give Him the glory, great things He hath done!", "Praise"),

    (7, "Blessed Assurance", "Fanny Crosby", "English",
     "Blessed assurance, Jesus is mine!\nOh, what a foretaste of glory divine!\nHeir of salvation, purchase of God,\nBorn of His Spirit, washed in His blood.\n\nChorus:\nThis is my story, this is my song,\nPraising my Savior all the day long;\nThis is my story, this is my song,\nPraising my Savior all the day long.\n\nPerfect submission, perfect delight,\nVisions of rapture now burst on my sight;\nAngels descending bring from above\nEchoes of mercy, whispers of love.\n\nPerfect submission, all is at rest,\nI in my Savior am happy and blest,\nWatching and waiting, looking above,\nFilled with His goodness, lost in His love.", "Assurance"),

    (8, "Rock of Ages", "Augustus Toplady", "English",
     "Rock of Ages, cleft for me,\nLet me hide myself in Thee;\nLet the water and the blood,\nFrom Thy riven side which flowed,\nBe of sin the double cure;\nSave from wrath and make me pure.\n\nNot the labor of my hands\nCan fulfill Thy law's demands;\nCould my zeal no respite know,\nCould my tears forever flow,\nAll for sin could not atone;\nThou must save, and Thou alone.\n\nNothing in my hand I bring,\nSimply to Thy cross I cling;\nNaked, come to Thee for dress;\nHelpless, look to Thee for grace;\nFoul, I to the fountain fly;\nWash me, Savior, or I die.", "Salvation"),

    (9, "It Is Well with My Soul", "Horatio Spafford", "English",
     "When peace like a river attendeth my way,\nWhen sorrows like sea billows roll,\nWhatever my lot, Thou hast taught me to say,\nIt is well, it is well with my soul.\n\nChorus:\nIt is well (it is well)\nWith my soul (with my soul)\nIt is well, it is well with my soul.\n\nThough Satan should buffet, though trials should come,\nLet this blest assurance control:\nThat Christ hath regarded my helpless estate,\nAnd hath shed His own blood for my soul.\n\nMy sin — oh, the bliss of this glorious thought! —\nMy sin, not in part, but the whole,\nIs nailed to the cross, and I bear it no more;\nPraise the Lord, praise the Lord, O my soul!\n\nAnd Lord, haste the day when my faith shall be sight,\nThe clouds be rolled back as a scroll:\nThe trump shall resound and the Lord shall descend;\nEven so — it is well with my soul.", "Peace"),

    (10, "Joyful, Joyful, We Adore Thee", "Henry van Dyke", "English",
     "Joyful, joyful, we adore Thee,\nGod of glory, Lord of love;\nHearts unfold like flow'rs before Thee,\nOp'ning to the sun above.\nMelt the clouds of sin and sadness;\nDrive the dark of doubt away;\nGiver of immortal gladness,\nFill us with the light of day!\n\nAll Thy works with joy surround Thee,\nEarth and heav'n reflect Thy rays,\nStars and angels sing around Thee,\nCenter of unbroken praise.\nField and forest, vale and mountain,\nFlow'ry meadow, flashing sea,\nChanting bird and flowing fountain,\nCall us to rejoice in Thee.", "Joy"),

    (11, "Nearer My God to Thee", "Sarah F. Adams", "English",
     "Nearer, my God, to Thee,\nNearer to Thee!\nE'en though it be a cross\nThat raiseth me;\nStill all my song shall be,\nNearer, my God, to Thee,\nNearer, my God, to Thee,\nNearer to Thee!\n\nThough like the wanderer,\nThe sun gone down,\nDarkness be over me,\nMy rest a stone;\nYet in my dreams I'd be\nNearer, my God, to Thee,\nNearer, my God, to Thee,\nNearer to Thee!\n\nThere let the way appear,\nSteps unto heav'n;\nAll that Thou sendest me,\nIn mercy giv'n;\nAngels to beckon me\nNearer, my God, to Thee,\nNearer, my God, to Thee,\nNearer to Thee!", "Devotion"),

    (12, "How Firm a Foundation", "John Rippon", "English",
     "How firm a foundation, ye saints of the Lord,\nIs laid for your faith in His excellent word!\nWhat more can He say than to you He hath said,\nTo you who for refuge to Jesus have fled?\n\nFear not, I am with thee; oh, be not dismayed,\nFor I am thy God and will still give thee aid;\nI'll strengthen thee, help thee, and cause thee to stand,\nUpheld by My righteous, omnipotent hand.\n\nWhen through the deep waters I call thee to go,\nThe rivers of sorrow shall not overflow;\nFor I will be with thee thy troubles to bless,\nAnd sanctify to thee thy deepest distress.\n\nThe soul that on Jesus hath leaned for repose,\nI will not, I will not desert to his foes;\nThat soul, though all hell should endeavor to shake,\nI'll never, no never, no never forsake!", "Faith"),

    (13, "Crown Him with Many Crowns", "Matthew Bridges", "English",
     "Crown Him with many crowns,\nThe Lamb upon His throne;\nHark! How the heavenly anthem drowns\nAll music but its own!\nAwake, my soul, and sing\nOf Him who died for thee,\nAnd hail Him as thy matchless King\nThrough all eternity.\n\nCrown Him the Lord of love;\nBehold His hands and side,\nRich wounds, yet visible above,\nIn beauty glorified.\nNo angel in the sky\nCan fully bear that sight,\nBut downward bends his wond'ring eye\nAt mysteries so bright.\n\nCrown Him the Lord of life,\nWho triumphed o'er the grave,\nAnd rose victorious in the strife\nFor those He came to save.\nHis glories now we sing\nWho died and rose on high,\nWho died eternal life to bring\nAnd lives that death may die.", "Majesty"),

    (14, "The Old Rugged Cross", "George Bennard", "English",
     "On a hill far away stood an old rugged cross,\nThe emblem of suff'ring and shame;\nAnd I love that old cross where the dearest and best\nFor a world of lost sinners was slain.\n\nChorus:\nSo I'll cherish the old rugged cross,\nTill my trophies at last I lay down;\nI will cling to the old rugged cross,\nAnd exchange it some day for a crown.\n\nO that old rugged cross, so despised by the world,\nHas a wondrous attraction for me;\nFor the dear Lamb of God left His glory above\nTo bear it to dark Calvary.\n\nIn the old rugged cross, stained with blood so divine,\nA wondrous beauty I see;\nFor 'twas on that old cross Jesus suffered and died\nTo pardon and sanctify me.\n\nTo the old rugged cross I will ever be true,\nIts shame and reproach gladly bear;\nThen He'll call me some day to my home far away,\nWhere His glory forever I'll share.", "Salvation"),

    (15, "I Surrender All", "Judson Van DeVenter", "English",
     "All to Jesus I surrender,\nAll to Him I freely give;\nI will ever love and trust Him,\nIn His presence daily live.\n\nChorus:\nI surrender all, I surrender all;\nAll to Thee, my blessed Savior,\nI surrender all.\n\nAll to Jesus I surrender,\nHumbly at His feet I bow;\nWorldly pleasures all forsaken,\nTake me, Jesus, take me now.\n\nAll to Jesus I surrender,\nMake me, Savior, wholly Thine;\nLet me feel the Holy Spirit,\nTruly know that Thou art mine.\n\nAll to Jesus I surrender,\nLord, I give myself to Thee;\nFill me with Thy love and power,\nLet Thy blessing fall on me.", "Consecration"),

    (16, "Count Your Blessings", "Johnson Oatman Jr.", "English",
     "When upon life's billows you are tempest-tossed,\nWhen you are discouraged, thinking all is lost,\nCount your many blessings, name them one by one,\nAnd it will surprise you what the Lord hath done.\n\nChorus:\nCount your blessings, name them one by one;\nCount your blessings, see what God hath done;\nCount your blessings, name them one by one;\nCount your many blessings, see what God hath done.\n\nAre you ever burdened with a load of care?\nDoes the cross seem heavy you are called to bear?\nCount your many blessings, every doubt will fly,\nAnd you will be singing as the days go by.\n\nSo amid the conflict, whether great or small,\nDo not be discouraged, God is over all;\nCount your many blessings, angels will attend,\nHelp and comfort give you to your journey's end.", "Gratitude"),

    (17, "Just As I Am", "Charlotte Elliott", "English",
     "Just as I am, without one plea,\nBut that Thy blood was shed for me,\nAnd that Thou bidd'st me come to Thee,\nO Lamb of God, I come! I come!\n\nJust as I am, and waiting not\nTo rid my soul of one dark blot,\nTo Thee whose blood can cleanse each spot,\nO Lamb of God, I come! I come!\n\nJust as I am, though tossed about\nWith many a conflict, many a doubt,\nFightings and fears within, without,\nO Lamb of God, I come! I come!\n\nJust as I am, Thou wilt receive,\nWilt welcome, pardon, cleanse, relieve;\nBecause Thy promise I believe,\nO Lamb of God, I come! I come!", "Salvation"),

    (18, "I Need Thee Every Hour", "Annie Hawks", "English",
     "I need Thee every hour, most gracious Lord;\nNo tender voice like Thine can peace afford.\n\nChorus:\nI need Thee, O I need Thee;\nEvery hour I need Thee!\nO bless me now, my Savior,\nI come to Thee.\n\nI need Thee every hour, stay Thou nearby;\nTemptations lose their power when Thou art nigh.\n\nI need Thee every hour, in joy or pain;\nCome quickly and abide, or life is vain.\n\nI need Thee every hour; teach me Thy will,\nAnd Thy rich promises in me fulfill.", "Dependence"),

    (19, "Leaning on the Everlasting Arms", "Elisha A. Hoffman", "English",
     "What a fellowship, what a joy divine,\nLeaning on the everlasting arms;\nWhat a blessedness, what a peace is mine,\nLeaning on the everlasting arms.\n\nChorus:\nLeaning, leaning,\nSafe and secure from all alarms;\nLeaning, leaning,\nLeaning on the everlasting arms.\n\nOh, how sweet to walk in this pilgrim way,\nLeaning on the everlasting arms;\nOh, how bright the path grows from day to day,\nLeaning on the everlasting arms.\n\nWhat have I to dread, what have I to fear,\nLeaning on the everlasting arms?\nI have blessed peace with my Lord so near,\nLeaning on the everlasting arms.", "Trust"),

    (20, "When the Roll Is Called Up Yonder", "James M. Black", "English",
     "When the trumpet of the Lord shall sound,\nAnd time shall be no more,\nAnd the morning breaks, eternal, bright and fair;\nWhen the saved of earth shall gather over on the other shore,\nAnd the roll is called up yonder, I'll be there.\n\nChorus:\nWhen the roll is called up yonder,\nWhen the roll is called up yonder,\nWhen the roll is called up yonder,\nWhen the roll is called up yonder, I'll be there.\n\nOn that bright and cloudless morning when the dead in Christ shall rise,\nAnd the glory of His resurrection share;\nWhen His chosen ones shall gather to their home beyond the skies,\nAnd the roll is called up yonder, I'll be there.\n\nLet us labor for the Master from the dawn till setting sun,\nLet us talk of all His wondrous love and care;\nThen when all of life is over, and our work on earth is done,\nAnd the roll is called up yonder, I'll be there.", "Heaven"),

    # ═══════════════ SWAHILI HYMNS ═══════════════
    (51, "Bwana ni Mchungaji Wangu", "Zaburi 23", "Swahili",
     "Bwana ni mchungaji wangu,\nSitapungukiwa na chochote.\nAnaniwezesha kulala mahali penye majani,\nAnaniongoza karibu na maji ya utulivu.\n\nAnaiburudisha roho yangu;\nAnaongoza kwenye njia za haki\nKwa ajili ya jina lake.\nHata nikipita katika bonde la uvuli wa mauti,\nSitaogopa mabaya; kwa maana Wewe uko pamoja nami.\n\nNako mkuki Wako na fimbo Yako,\nVitu hivi vinanipa faraja.\nUnatayarisha meza mbele yangu\nMbele za adui zangu.\n\nUnajaza kichwa changu mafuta;\nKikombe changu kinafurka.\nHakika wema na rehema vitanifuata\nSiku zote za maisha yangu;\nNami nitakaa katika nyumba ya Bwana\nMilele na milele.", "Imani"),

    (52, "Mungu ni Mwema", "Wimbo wa Kanisa", "Swahili",
     "Mungu ni mwema, ndiyo mwema,\nAmetendea wema nami.\nMungu ni mwema, ndiyo mwema,\nAmetendea wema nami.\n\nNilikuwa mgonjwa, Yeye aliniponya,\nNilikuwa na huzuni, Yeye alinifurahi.\nNilikuwa na njaa, Yeye alinilisha,\nAmetendea wema nami.\n\nNilikuwa mfungwa, Yeye aliniachilia huru,\nNilikuwa mpotovu, Yeye alinirudisha.\nNilikuwa mauti, Yeye alinihuisha,\nAmetendea wema nami.\n\nMungu ni mwema, ndiyo mwema,\nAmetendea wema nami.\nMungu ni mwema, ndiyo mwema,\nAmetendea wema nami.", "Sifa"),

    (53, "Yesu ni Rafiki Yangu", "Joseph Scriven (tafsiri)", "Swahili",
     "Yesu ni rafiki yangu,\nYeye hubeba mzigo wangu;\nNi neema ya ajabu\nKukimbilia kwake kwa maombi.\nTwapoteza amani nyingi,\nTwachukua maumivu mengi,\nKwa sababu hatuendei\nKila kitu kwa Mungu kwa sala.\n\nJe, tuna majaribu na vishawishi?\nJe, kuna shida mahali?\nTusikate tamaa kamwe,\nHebu twendee Bwana kwa sala.\nMwanafunzi mwenye uaminifu,\nAtashiriki huzuni zetu;\nYesu anajua udhaifu wetu,\nHebu twendee Bwana kwa sala.\n\nJe, tuna huzuni na mzigo wa wasiwasi?\nMkimbilio wetu ni Kristo;\nHebu twendee Bwana kwa sala.\nMarafiki wanatuacha, wanatupotoka?\nTwendee Bwana kwa sala!\nKatika mikono Yake atatulinda;\nUtulivu tutaupata hapo.", "Sala"),

    (54, "Niko Salama", "Wimbo wa Kanisa", "Swahili",
     "Niko salama mikononi mwa Yesu,\nNiko salama, si hofu yangu;\nMaisha ya neema yananihusu,\nNiko salama mikononi mwa Bwana.\n\nKimbilio langu ni Kristo Yesu,\nNguvu zangu ni Mwokozi wangu;\nYeye ni ulinzi wangu dhidi ya shetani,\nNiko salama milele nawe.\n\nChorus:\nNiko salama, niko salama,\nMikononi mwa Bwana Yesu.\nNiko salama, niko salama,\nMikononi mwa Mwokozi wangu.", "Usalama"),

    (55, "Shangilia Bwana", "Wimbo wa Furaha", "Swahili",
     "Shangilia Bwana, shirikiana wimbo,\nMpe Mungu sifa zake zote.\nInua sauti yako juu ya mbingu,\nMpe Bwana utukufu wake.\n\nKwa sauti ya furaha tumwimbie Bwana,\nTwende mbele zake kwa shukrani.\nKwa sababu Bwana ni Mungu mkuu,\nMfalme mkuu kuliko miungu yote.\n\nChorus:\nShangilia! Shangilia! Shangilia Bwana!\nSifa zote ni zake Mungu wetu.\nShangilia! Shangilia! Shangilia Bwana!\nMpe Mungu utukufu wake wote.", "Sifa"),

    (56, "Kwa Neema Nimeokolewa", "Wimbo wa Neema", "Swahili",
     "Kwa neema nimeokolewa,\nSio kwa matendo yangu;\nKwa imani ya moyo wangu,\nNimepata wokovu huu.\n\nKwa damu ya Yesu Kristo,\nDhambi zangu zimeoshwa;\nKwa upendo wake mkubwa,\nNimepata uzima huu.\n\nChorus:\nNeema! Neema ya Mungu!\nNimeokolewa kwa neema;\nSio kwa nguvu zangu mwenyewe,\nBali kwa neema ya Mungu.", "Neema"),

    (57, "Tembea na Yesu", "Wimbo wa Imani", "Swahili",
     "Tembea na Yesu kila siku,\nYeye ataongoza njia yako;\nJa angalieni mbele yako,\nYeye atakulinda siku zote.\n\nTembea na Yesu usiku na mchana,\nUsimwache upweke wako;\nYeye ni mwanga wa njia yako,\nTembea naye siku zote.\n\nChorus:\nTembea, tembea na Yesu,\nTembea naye siku zote;\nYeye ni rafiki wa kweli,\nTembea naye kila wakati.", "Ufuataji"),

    (58, "Nguvu Zangu ni Bwana", "Wimbo wa Nguvu", "Swahili",
     "Nguvu zangu ni Bwana,\nMimi si dhaifu tena;\nYeye hunipa nguvu,\nKila siku ya maisha.\n\nWakati wa dhiki na huzuni,\nYeye yupo pamoja nami;\nAnanipatia nguvu mpya,\nKila wakati ninalohitaji.\n\nChorus:\nBwana ni nguvu zangu na wimbo wangu,\nAmekuwa wokovu wangu;\nYeye ni Mungu wangu, nitamsifu,\nMungu wa baba zangu, nitamtukuza.", "Nguvu"),

    (59, "Hakuna Mungu Kama Wewe", "Wimbo wa Ibada", "Swahili",
     "Hakuna Mungu kama Wewe,\nHakuna mwingine kama Wewe;\nWewe ni Mungu wa milele,\nBwana wa mabwana wote.\n\nWewe ni mkweli na mwaminifu,\nHuruma Yako haishindwi;\nUpendo Wako unadumu milele,\nHakuna mwingine kama Wewe.\n\nChorus:\nHakuna, hakuna, hakuna kama Wewe;\nHakuna Mungu kama Wewe Bwana;\nHakuna, hakuna, hakuna kama Wewe;\nWewe peke yako ndiye Mungu.", "Ibada"),

    (60, "Baba Yetu Mbinguni", "Sala ya Bwana", "Swahili",
     "Baba yetu uliye mbinguni,\nJina Lako litukuzwe;\nUfalme Wako uje,\nMapenzi Yako yatimizwe,\nHapa duniani kama mbinguni.\n\nTupe leo mkate wetu wa kila siku,\nUtusamehe dhambi zetu,\nKama sisi tunavyowasamehe\nWalio na dhambi juu yetu.\n\nUsitutie katika majaribu,\nBali utuokoe na yule mwovu;\nKwa maana Ufalme ni Wako,\nNa nguvu na utukufu,\nMilele na milele. Amina.", "Sala"),

    (61, "Ee Mungu wa Mbinguni", "Wimbo wa Mapambazuko", "Swahili",
     "Ee Mungu wa mbinguni,\nTunaposimama mbele Yako;\nTunaomba msamaha Wako,\nKwa dhambi zetu zote.\n\nSisi ni watoto Wako,\nTunahitaji msaada Wako;\nTuongoze kwa nuru Yako,\nSiku zote za maisha yetu.\n\nChorus:\nEe Mungu, ee Mungu,\nTukufu na nguvu ni Zako;\nEe Mungu, ee Mungu,\nSisi ni wako milele.", "Ibada"),

    (62, "Yesu Ametuokoa", "Wimbo wa Wokovu", "Swahili",
     "Yesu ametuokoa,\nKwa damu yake ya thamani;\nAmebeba dhambi zetu,\nPamoja na huzuni zetu.\n\nKwa upendo wake mkubwa,\nAlikufa msalabani;\nAlifufuka siku ya tatu,\nAli mshindi wa mauti.\n\nChorus:\nSifa na heshima kwa Yesu,\nMwokozi wa ulimwengu;\nAmina! Amina! Amina!\nSifa kwa Mwana wa Mungu.", "Wokovu"),

    (63, "Ninaomba Nguvu Zako", "Wimbo wa Maombi", "Swahili",
     "Ninaomba nguvu Zako, Bwana,\nKila siku ya maisha yangu;\nNipe nguvu za kukushinda,\nMajaribu yote ninayokutana nayo.\n\nNinaomba nuru Yako, Bwana,\nIniendelee kila wakati;\nNiongoze kwenye njia ya kweli,\nMbali na giza na dhambi.\n\nChorus:\nNipe nguvu, nipe nguvu,\nNipe nguvu Bwana Yesu;\nNipe nguvu, nipe nguvu,\nKupigana vita vyako.", "Maombi"),

    # ═══════════════ KIKUYU HYMNS ═══════════════
    (101, "Ngai ni Mũtungi Wakwa", "Gĩtaara 23", "Kikuyu",
     "Ngai nĩ mũtungi wakwa,\nNdingĩkorwo na ũhoro.\nAnĩenyeria gũkũrũkia thĩĩni wa mĩtitu,\nArĩ hamwe na mĩto ya ũtuĩku.\n\nNĩandĩĩtia mũhuro mũega,\nNĩandonya maaĩ ma ũtuĩku.\nNĩathurũra mũoyo wakwa,\nNĩanyihĩa njĩra ya ũgĩo.\n\nO nĩ akinyite na thĩĩ wa gĩthĩĩ kĩa ĩfu,\nNdingĩogopa ũũru;\nNĩwe ũrĩ hamwe na niĩ.\nRũthĩ rwako na ithanĩ rĩako,\nNĩĩ nĩarĩgaĩrĩria.\n\nNgai nĩ mwega, nĩ mwathani wakwa,\nNĩwe mũhonokia wakwa;\nAhoya wakwa ngĩũmiĩra,\nNginya rĩrĩa nĩngathie.", "Ũhoya"),

    (102, "Nĩ Wendo wa Ngai", "Nyĩmbo ya Ngai", "Kikuyu",
     "Nĩ wendo wa Ngai mũnene,\nŨndũ wa kumanahio;\nWendo ũcio ũtheriire njĩra,\nNa Jesu nĩathirĩirie.\n\nNgai nĩatumire Mwana wake,\nKũrĩkia tũhoro twetu;\nNĩarutire magua gake,\nNĩatugũtĩire thĩĩ.\n\nChorus:\nNĩ wendo, nĩ wendo,\nWendo wa Ngai tũcariria.\nNĩ wendo, nĩ wendo,\nWendo wake nĩ wa rĩrĩa.", "Wendo"),

    (103, "Tũthaitha Ngai", "Nyĩmbo ya Gũthaithia", "Kikuyu",
     "Tũthaitha Ngai kĩrĩa kĩothe,\nTwĩhe ũhoro na thayũ wake;\nArĩ hĩndĩ ciothe hamwe na tũĩ,\nNĩwe Ngai wa rĩĩtwa rĩa Jesu.\n\nTũthaithia na ngoro ciothe,\nTwĩhe ũhoro wake ũcio;\nTũmwariire rĩĩtwa rĩake,\nNgai mwathani wa ĩtũĩ ciothe.\n\nChorus:\nThaithia, thaithia Ngai,\nThaitha na ngoro yothe;\nThaithia, thaithia Ngai,\nNĩwe ũrĩ mwega kĩrĩa kĩothe.", "Gũthaithia"),

    (104, "Jesu Ndĩ Rafiki Wakwa", "Nyĩmbo ya Ũhĩĩkano", "Kikuyu",
     "Jesu ndĩ rafiki wakwa mwega,\nNĩaruta mĩrũku yakwa yothe;\nNĩ ũngũ wa kũhĩĩkana nake,\nKũgũtĩra ũhoro kũrĩ Ngai.\n\nGĩkĩ kĩndũ tũkoria,\nŨhoro ũrĩa tũngikorire;\nTũhĩĩkane na Jesu Kristo,\nNĩwe ũgaatũhonokia.\n\nChorus:\nJesu, Jesu ndĩ rafiki wakwa,\nNĩwe ũrĩ hamwe na niĩ;\nJesu, Jesu ndĩ rafiki wakwa,\nNĩwe ũhonokia wakwa.", "Ũhĩĩkano"),

    (105, "Ngai Nĩ Mwega", "Nyĩmbo ya Gũcokia Ĩthĩmũ", "Kikuyu",
     "Ngai nĩ mwega, ĩĩ nĩ mwega,\nNĩandĩtĩire wega niĩ.\nNgai nĩ mwega, ĩĩ nĩ mwega,\nNĩandĩtĩire wega niĩ.\n\nNdĩarĩĩ, Ngai nĩaninuirie;\nNdĩ na ĩkera, Ngai nĩanĩfurĩirie.\nNdĩ na njĩra ĩrĩa mbũrũ,\nJesu nĩanĩonyeire njĩra ya ũgĩo.\n\nNgai nĩ mwega, ĩĩ nĩ mwega,\nNĩandĩtĩire wega niĩ.\nNgai nĩ mwega, ĩĩ nĩ mwega,\nNĩandĩtĩire wega niĩ.", "Gũcokia Ĩthĩmũ"),

    (106, "Rĩĩtwa Rĩa Jesu", "Nyĩmbo ya Rĩĩtwa", "Kikuyu",
     "Rĩĩtwa rĩa Jesu nĩ rĩega,\nMũhonokia na mũtiĩrĩri;\nKĩrĩa kĩothe tũthingatire,\nNa rĩĩtwa rĩake rĩa nguvu.\n\nRĩĩtwa rĩa Jesu nĩ nguvu,\nRĩĩtwa rĩake nĩ ũhoro;\nRĩĩtwa rĩake rĩtugũhonokia,\nRĩĩtwa rĩake rĩ rĩa hĩndĩ ciothe.\n\nChorus:\nJesu, Jesu, rĩĩtwa rĩa nguvu;\nJesu, Jesu, mũhonokia witu;\nJesu, Jesu, ũgaatũhonokia,\nRĩĩtwa rĩake nĩ rĩa ũgĩo.", "Rĩĩtwa"),

    (107, "Jesu Nĩatuhetĩkia", "Nyĩmbo ya Ũhonoki", "Kikuyu",
     "Jesu nĩatuhetĩkia kũgarũrwo,\nNa thakame yake ya ũtuĩku;\nNĩarũtĩire mĩrũku yetu yothe,\nNa mahinda ma ũrĩa ũtaagĩrĩrio.\n\nKwa wendo wake mũnene,\nNĩathirĩirie muĩ wa msalaba;\nNĩafũkũrwo na mũthenya wa gathatũ,\nNĩaathima maũndũ ma thĩ.\n\nChorus:\nĨthĩmũ na heshima kũrĩ Jesu,\nMũhonokia wa thĩ yothe;\nAmina! Amina! Amina!\nĨthĩmũ kũrĩ Mwana wa Ngai.", "Ũhonoki"),

    (108, "Tũgĩe na Ngai", "Nyĩmbo ya Gũtũĩkana", "Kikuyu",
     "Tũgĩe na Ngai hĩndĩ ciothe,\nTwĩte kũrĩ maũndũ make;\nArĩ mwathani wa njĩra yetu,\nNĩwe ũgaatũĩka mwega.\n\nTũgĩe na Ngai na ngoro ciothe,\nTwĩhe ũhoro wake mũega;\nArĩ hamwe na tũĩ kĩrĩa kĩothe,\nNĩwe ũrĩ mũhonokia witu.\n\nChorus:\nGĩa na Ngai, gĩa na Ngai,\nGĩa na Ngai hĩndĩ ciothe;\nGĩa na Ngai, gĩa na Ngai,\nNĩwe ũgaatũhonokia.", "Gũtũĩkana"),
]


class Command(BaseCommand):
    help = 'Load hymns (English, Swahili, Kikuyu) into the database'

    def add_arguments(self, parser):
        parser.add_argument('--update', action='store_true', help='Update existing hymns with new data')

    def handle(self, *args, **options):
        created = skipped = updated = 0
        for item in HYMNS_DATA:
            number, title, author, language, lyrics, category = item
            existing = Hymn.objects.filter(number=number).first()
            if existing:
                if options.get('update'):
                    existing.title = title
                    existing.author = author
                    existing.language = language
                    existing.lyrics = lyrics
                    existing.category = category
                    existing.save()
                    updated += 1
                else:
                    skipped += 1
            else:
                Hymn.objects.create(
                    number=number, title=title, author=author,
                    language=language, lyrics=lyrics, category=category
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Hymns: {created} added, {updated} updated, {skipped} already existed.'
        ))
        totals = {}
        for h in Hymn.objects.all():
            totals[h.language] = totals.get(h.language, 0) + 1
        for lang, count in totals.items():
            self.stdout.write(f'  {lang}: {count} hymns')

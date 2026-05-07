from django.core.management.base import BaseCommand
from myapp.models import Hymn


HYMNS_DATA = [
    (1, "Holy, Holy, Holy", "Reginald Heber",
     "Holy, holy, holy! Lord God Almighty!\nEarly in the morning our song shall rise to Thee;\nHoly, holy, holy! Merciful and mighty!\nGod in three Persons, blessed Trinity!\n\nHoly, holy, holy! All the saints adore Thee,\nCasting down their golden crowns around the glassy sea;\nCherubim and seraphim falling down before Thee,\nWho wert, and art, and evermore shalt be.\n\nHoly, holy, holy! Though the darkness hide Thee,\nThough the eye of sinful man Thy glory may not see;\nOnly Thou art holy; there is none beside Thee,\nPerfect in pow'r, in love, and purity.\n\nHoly, holy, holy! Lord God Almighty!\nAll Thy works shall praise Thy name in earth, and sky, and sea;\nHoly, holy, holy! Merciful and mighty!\nGod in three Persons, blessed Trinity!", "Praise"),

    (2, "Amazing Grace", "John Newton",
     "Amazing grace! How sweet the sound\nThat saved a wretch like me!\nI once was lost, but now am found;\nWas blind, but now I see.\n\n'Twas grace that taught my heart to fear,\nAnd grace my fears relieved;\nHow precious did that grace appear\nThe hour I first believed.\n\nThrough many dangers, toils and snares,\nI have already come;\n'Tis grace hath brought me safe thus far,\nAnd grace will lead me home.\n\nThe Lord has promised good to me,\nHis Word my hope secures;\nHe will my Shield and Portion be,\nAs long as life endures.\n\nWhen we've been there ten thousand years,\nBright shining as the sun,\nWe've no less days to sing God's praise\nThan when we'd first begun.", "Grace"),

    (3, "How Great Thou Art", "Carl Boberg",
     "O Lord my God! When I in awesome wonder\nConsider all the worlds Thy hands have made,\nI see the stars, I hear the rolling thunder,\nThy pow'r throughout the universe displayed.\n\nChorus:\nThen sings my soul, my Saviour God, to Thee:\nHow great Thou art! How great Thou art!\nThen sings my soul, my Saviour God, to Thee:\nHow great Thou art! How great Thou art!\n\nWhen through the woods and forest glades I wander\nAnd hear the birds sing sweetly in the trees;\nWhen I look down from lofty mountain grandeur\nAnd hear the brook and feel the gentle breeze.\n\nAnd when I think that God, His Son not sparing,\nSent Him to die, I scarce can take it in;\nThat on the cross, my burden gladly bearing,\nHe bled and died to take away my sin.\n\nWhen Christ shall come with shout of acclamation\nAnd take me home, what joy shall fill my heart!\nThen I shall bow in humble adoration\nAnd there proclaim, my God, how great Thou art!", "Praise"),

    (4, "Great Is Thy Faithfulness", "Thomas O. Chisholm",
     "Great is Thy faithfulness, O God my Father;\nThere is no shadow of turning with Thee;\nThou changest not, Thy compassions, they fail not;\nAs Thou hast been, Thou forever will be.\n\nChorus:\nGreat is Thy faithfulness! Great is Thy faithfulness!\nMorning by morning new mercies I see.\nAll I have needed Thy hand hath provided;\nGreat is Thy faithfulness, Lord, unto me!\n\nSummer and winter and springtime and harvest,\nSun, moon and stars in their courses above\nJoin with all nature in manifold witness\nTo Thy great faithfulness, mercy and love.\n\nPardon for sin and a peace that endureth,\nThine own dear presence to cheer and to guide,\nStrength for today and bright hope for tomorrow —\nBlessings all mine, with ten thousand beside!", "Faithfulness"),

    (5, "What a Friend We Have in Jesus", "Joseph M. Scriven",
     "What a friend we have in Jesus,\nAll our sins and griefs to bear!\nWhat a privilege to carry\nEverything to God in prayer!\nOh, what peace we often forfeit,\nOh, what needless pain we bear,\nAll because we do not carry\nEverything to God in prayer!\n\nHave we trials and temptations?\nIs there trouble anywhere?\nWe should never be discouraged;\nTake it to the Lord in prayer!\nCan we find a friend so faithful,\nWho will all our sorrows share?\nJesus knows our every weakness;\nTake it to the Lord in prayer!\n\nAre we weak and heavy-laden,\nCumbered with a load of care?\nPrecious Savior, still our refuge —\nTake it to the Lord in prayer!\nDo thy friends despise, forsake thee?\nTake it to the Lord in prayer!\nIn His arms He'll take and shield thee;\nThou wilt find a solace there.", "Prayer"),

    (6, "To God Be the Glory", "Fanny Crosby",
     "To God be the glory, great things He hath taught us,\nGreat things He hath done, and great our rejoicing\nThrough Jesus the Son;\nBut purer and higher and greater will be\nOur wonder, our transport, when Jesus we see.\n\nChorus:\nPraise the Lord! Praise the Lord!\nLet the earth hear His voice!\nPraise the Lord! Praise the Lord!\nLet the people rejoice!\nO come to the Father through Jesus the Son,\nAnd give Him the glory, great things He hath done!", "Praise"),

    (7, "Blessed Assurance", "Fanny Crosby",
     "Blessed assurance, Jesus is mine!\nOh, what a foretaste of glory divine!\nHeir of salvation, purchase of God,\nBorn of His Spirit, washed in His blood.\n\nChorus:\nThis is my story, this is my song,\nPraising my Savior all the day long;\nThis is my story, this is my song,\nPraising my Savior all the day long.\n\nPerfect submission, perfect delight,\nVisions of rapture now burst on my sight;\nAngels descending bring from above\nEchoes of mercy, whispers of love.\n\nPerfect submission, all is at rest,\nI in my Savior am happy and blest,\nWatching and waiting, looking above,\nFilled with His goodness, lost in His love.", "Assurance"),

    (8, "Rock of Ages", "Augustus Toplady",
     "Rock of Ages, cleft for me,\nLet me hide myself in Thee;\nLet the water and the blood,\nFrom Thy riven side which flowed,\nBe of sin the double cure;\nSave from wrath and make me pure.\n\nNot the labor of my hands\nCan fulfill Thy law's demands;\nCould my zeal no respite know,\nCould my tears forever flow,\nAll for sin could not atone;\nThou must save, and Thou alone.\n\nNothing in my hand I bring,\nSimply to Thy cross I cling;\nNaked, come to Thee for dress;\nHelpless, look to Thee for grace;\nFoul, I to the fountain fly;\nWash me, Savior, or I die.", "Salvation"),

    (9, "Joyful, Joyful, We Adore Thee", "Henry van Dyke",
     "Joyful, joyful, we adore Thee,\nGod of glory, Lord of love;\nHearts unfold like flow'rs before Thee,\nOp'ning to the sun above.\nMelt the clouds of sin and sadness;\nDrive the dark of doubt away;\nGiver of immortal gladness,\nFill us with the light of day!\n\nAll Thy works with joy surround Thee,\nEarth and heav'n reflect Thy rays,\nStars and angels sing around Thee,\nCenter of unbroken praise.\nField and forest, vale and mountain,\nFlow'ry meadow, flashing sea,\nChanting bird and flowing fountain,\nCall us to rejoice in Thee.", "Joy"),

    (10, "It Is Well with My Soul", "Horatio Spafford",
     "When peace like a river attendeth my way,\nWhen sorrows like sea billows roll,\nWhatever my lot, Thou hast taught me to say,\n\"It is well, it is well with my soul.\"\n\nChorus:\nIt is well (it is well)\nWith my soul (with my soul)\nIt is well, it is well with my soul.\n\nThough Satan should buffet, though trials should come,\nLet this blest assurance control:\nThat Christ hath regarded my helpless estate,\nAnd hath shed His own blood for my soul.\n\nMy sin — oh, the bliss of this glorious thought! —\nMy sin, not in part, but the whole,\nIs nailed to the cross, and I bear it no more;\nPraise the Lord, praise the Lord, O my soul!\n\nAnd Lord, haste the day when my faith shall be sight,\nThe clouds be rolled back as a scroll:\nThe trump shall resound and the Lord shall descend;\n\"Even so\" — it is well with my soul.", "Peace"),

    (11, "Nearer My God to Thee", "Sarah F. Adams",
     "Nearer, my God, to Thee,\nNearer to Thee!\nE'en though it be a cross\nThat raiseth me;\nStill all my song shall be,\nNearer, my God, to Thee,\nNearer, my God, to Thee,\nNearer to Thee!\n\nThough like the wanderer,\nThe sun gone down,\nDarkness be over me,\nMy rest a stone;\nYet in my dreams I'd be\nNearer, my God, to Thee,\nNearer, my God, to Thee,\nNearer to Thee!", "Devotion"),

    (12, "How Firm a Foundation", "John Rippon",
     "How firm a foundation, ye saints of the Lord,\nIs laid for your faith in His excellent word!\nWhat more can He say than to you He hath said,\nTo you who for refuge to Jesus have fled?\n\n\"Fear not, I am with thee; oh, be not dismayed,\nFor I am thy God and will still give thee aid;\nI'll strengthen thee, help thee, and cause thee to stand,\nUpheld by My righteous, omnipotent hand.\n\n\"When through the deep waters I call thee to go,\nThe rivers of sorrow shall not overflow;\nFor I will be with thee thy troubles to bless,\nAnd sanctify to thee thy deepest distress.\n\nThe soul that on Jesus hath leaned for repose,\nI will not, I will not desert to his foes;\nThat soul, though all hell should endeavor to shake,\nI'll never, no never, no never forsake!\"", "Faith"),

    (13, "O Worship the King", "Robert Grant",
     "O worship the King all-glorious above,\nO gratefully sing His power and His love;\nOur Shield and Defender, the Ancient of Days,\nPavilioned in splendor, and girded with praise.\n\nO tell of His might, O sing of His grace,\nWhose robe is the light, whose canopy space.\nHis chariots of wrath the deep thunderclouds form,\nAnd dark is His path on the wings of the storm.\n\nThy bountiful care what tongue can recite?\nIt breathes in the air, it shines in the light;\nIt streams from the hills, it descends to the plain,\nAnd sweetly distils in the dew and the rain.", "Worship"),

    (14, "There Is a Fountain", "William Cowper",
     "There is a fountain filled with blood\nDrawn from Immanuel's veins;\nAnd sinners plunged beneath that flood\nLose all their guilty stains.\nLose all their guilty stains,\nLose all their guilty stains;\nAnd sinners plunged beneath that flood\nLose all their guilty stains.\n\nThe dying thief rejoiced to see\nThat fountain in his day;\nAnd there have I, as vile as he,\nWashed all my sins away.", "Redemption"),

    (15, "Crown Him with Many Crowns", "Matthew Bridges",
     "Crown Him with many crowns,\nThe Lamb upon His throne;\nHark! How the heavenly anthem drowns\nAll music but its own!\nAwake, my soul, and sing\nOf Him who died for thee,\nAnd hail Him as thy matchless King\nThrough all eternity.\n\nCrown Him the Lord of life,\nWho triumphed o'er the grave,\nAnd rose victorious in the strife\nFor those He came to save.\nHis glories now we sing\nWho died and rose on high,\nWho died eternal life to bring\nAnd lives that death may die.", "Majesty"),
]


class Command(BaseCommand):
    help = 'Load initial hymns into the database'

    def handle(self, *args, **options):
        created = 0
        skipped = 0
        for number, title, author, lyrics, category in HYMNS_DATA:
            _, is_new = Hymn.objects.get_or_create(
                number=number,
                defaults={'title': title, 'author': author, 'lyrics': lyrics, 'category': category}
            )
            if is_new:
                created += 1
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {created} new hymns. {skipped} already existed."
        ))

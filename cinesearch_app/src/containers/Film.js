import React from 'react';
import {
    Alert,
    Cell,
    CellButton,
    Div,
    FixedLayout,
    Footer,
    Group,
    HeaderButton,
    HeaderContext,
    HorizontalScroll,
    List,
    Panel,
    PanelHeader,
    PanelHeaderContent,
    platform,
    ScreenSpinner,
    View,
    Button
} from '@vkontakte/vkui';

import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import Typography from "@material-ui/core/Typography";
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import "../css/FilmPage.css"
import Icon24PlaySpeed from '@vkontakte/icons/dist/24/play_speed';
import ActorCard from "../components/ActorCard";
import Fab from "@material-ui/core/Fab";

export default class Home extends React.Component {
    constructor(props) {
        super(props);
        // this.store = props.store;
        // this.dispatch = props.dispatch;

        this.state = {
            youtube: false,
            film_id: props.film_id,
            title: "Мстители 4",

            youtubeurl: "https://www.youtube.com/embed/" + "gbcVZgO4n4E",
            photo: "https://www.wallpaperup.com/uploads/wallpapers/2018/03/22/1234615/3d0e59d12222626b5f8c7de5c77c8549-1000.jpg",
            plot: "Локи, сводный брат Тора, возвращается, и в этот раз он не один. Земля на грани порабощения, и только лучшие из лучших могут спасти человечество.\n" +
                "\n" +
                "Ник Фьюри, глава международной организации Щ. И. Т., собирает выдающихся поборников справедливости и добра, чтобы отразить атаку. Под предводительством Капитана Америки Железный Человек, Тор, Невероятный Халк, Соколиный глаз и Чёрная Вдова вступают в войну с захватчиком.",
            info: {
                "Год выпуска": "2012",
                "слоган": "«Avengers Assemble!»",
                "бюджет": "$220 000 000",
                "сборы в США": "$623 357 910"
            },
            actors: [{
                name: "Джони Деп",
                href: "https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BF%D0%BF,_%D0%94%D0%B6%D0%BE%D0%BD%D0%BD%D0%B8",
                photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/JohnnyDepp2018.jpg/600px-JohnnyDepp2018.jpg"
            }, {
                name: "Джони Деп",
                href: "https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BF%D0%BF,_%D0%94%D0%B6%D0%BE%D0%BD%D0%BD%D0%B8",
                photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/JohnnyDepp2018.jpg/600px-JohnnyDepp2018.jpg"
            }, {
                name: "Джони Деп",
                href: "https://ru.wikipedia.org/wiki/%D0%94%D0%B5%D0%BF%D0%BF,_%D0%94%D0%B6%D0%BE%D0%BD%D0%BD%D0%B8",
                photo: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/JohnnyDepp2018.jpg/600px-JohnnyDepp2018.jpg"
            }],
            comments: [
                {
                    name: "Сальнокова Елена",
                    stars: 3,
                    comment: "Очень крутой фильм, с большим удовольствием сходила бы еще раз. Отлично првели время всей семьей"
                }, {
                    name: "Михальцов Даниил",
                    stars: 6,
                    comment: "Сценарий так себе, но Робер Дауни тянит весь фильм"
                }
            ]

        };
        this.youtubeRef = React.createRef();
        this.android = platform() == "android";

    }

    createActors = () => {

        var rlist = [];
        var actors = this.state.actors;

        for (let i in actors) {
            let item = actors[i];
            //Create the parent and add the children
            // try {
            try {
                if (item)
                    rlist.push(
                        <ActorCard
                            {...item} />
                    );
            } catch (e) {
                console.log("Error write post")
            }
        }
        return rlist;
    };


    comments = () => {

        var rlist = [];
        var comments = this.state.comments;

        for (let i in comments) {
            let item = comments[i];
            //Create the parent and add the children
            // try {
            try {
                if (item)
                    rlist.push(
                        <div>
                            <Cell description={item.comment} multiline className={"comment"}
                                  asideContent={<div>{item.stars}/10</div>}>
                                {item.name}
                            </Cell>
                            {i < comments.length - 1 && <hr/>}
                        </div>
                    );
            } catch (e) {
                console.log("Error write post")
            }
        }
        return rlist;
    };
    showyotube = () => {

        var elem = document.getElementById("myvideo");
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) {
            elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        }
        var url = this.state.youtube;

        document.addEventListener('fullscreenchange', (event) => {
            // document.fullscreenElement will point to the element that
            // is in fullscreen mode if there is one. If not, the value
            // of the property is null.
            if (document.fullscreenElement) {
            } else {
                // document.exitFullscreen();
                elem.click();
                elem.src = "";
                elem.src = url;
            }
        });


    };
    info = () => {
        var ar = [];
        var info = this.state.info;
        for (var i in Object.keys(info)) {
            ar.push(
                <Cell before={Object.keys(info)[i]} asideContent={info[Object.keys(info)[i]]}/>
            )
        }
        return ar;
    };
    showTreiler = () => {
        if (this.state.youtube) {
            setTimeout(() => {
                this.setState({
                    youtube: false
                })
            }, 1000)
            document.getElementById("youtube").style.animation = " goout 1s ease";
        } else {
            console.log("OPEN Y")

            this.setState({
                youtube: true
            });
            // document.getElementById("youtube").style.animation="openYoutube 1s ease";

        }

    };


    render() {
        //upload our records

        return (
            <div className={"FilmContainer"}>
                {/*<FixedLayout>*/}
                <Fab
                    color="secondary"
                    variant="extended"
                    onClick={this.showTreiler}
                    style={{
                        position: "absolute",
                        "z-index": this.state.youtube && "2"
                    }}
                    className={"floatTip"}>
                    <Icon24PlaySpeed/>
                    Трейлер
                </Fab>

                <img className={"filmcover"} src={this.state.photo} id={"avatr"}/>
                {this.state.youtube &&
                <div style={{position: "absolute"}}
                     id={"youtube"}
                     className={"card_youtube"}>
                    <iframe src={this.state.youtubeurl}
                            style={{
                                height: document.getElementById("avatr").offsetHeight
                            }}
                            className={"film_card_youtube"}
                            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen/>
                </div>
                }

                <Group className={"block"}>
                    <ExpansionPanel>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon/>}>
                            <Typography>Сюжет фильма</Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Typography>
                                {this.state.plot}
                            </Typography>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>
                </Group>
                <Group title={"Информация"}>
                    {
                        this.info()
                    }
                    {/*<Cell before={"Год выпуска"} asideContent={"2012"}/>*/}
                </Group>
                <Group>
                    <Div style={
                        {
                            display: 'flex',
                        }}>
                        <Button size="l" stretched onClick={() => this.openURL(this.state.url1)}
                                className={"KinoPoisk"} style={{marginRight: 8}}>Кинопоиск</Button>

                        <Button size="l" stretched onClick={() => this.openURL(this.state.url2)}
                                className={"IVI"}> IVI</Button>
                    </Div>
                </Group>
                <Group title={"Актеры"}>
                    <HorizontalScroll>
                        <div style={{display: 'flex'}}>
                            {
                                this.createActors()
                            }
                        </div>
                    </HorizontalScroll>
                </Group>

                <Group title={"Отзывы"}>
                    {this.comments()}
                </Group>


            </div>


        )
    }
}



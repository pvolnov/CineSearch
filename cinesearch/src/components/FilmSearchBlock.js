import React from 'react';
import {
    Alert,
    Button,
    Cell,
    CellButton,
    Div,
    Footer,
    Group,
    HeaderButton,
    HeaderContext,
    List,
    Panel,
    PanelHeader,
    PanelHeaderContent,
    platform,
    ScreenSpinner,
    View
} from '@vkontakte/vkui';

import Card from "@material-ui/core/Card";
import Icon24PlaySpeed from '@vkontakte/icons/dist/24/play_speed';
import "../css/FilmSearchBlock.css";

import FastAverageColor from 'fast-average-color';
import Fab from "@material-ui/core/Fab";
import Icon24Favorite from '@vkontakte/icons/dist/24/favorite';
import Icon24FavoriteOutline from '@vkontakte/icons/dist/24/favorite_outline';

export default class FilmBlock extends React.Component {
    constructor(props) {
        super(props);
        this.parent = props.main;

        // this.store = props.store;
        // this.dispatch = props.dispatch;

        this.state = {
            actPanel: "menu",//active panel
            film_id: props.film_id,
            stars: 7,
            id: props.id,//view id
            popuot: null,
            youtube: false,
            avatar: "https://files.catbox.moe/xq7ghw.jpg",
            url1: "https://files.catbox.moe/xq7ghw.jpg",
            url2: "https://files.catbox.moe/xq7ghw.jpg",
            name: "Капитан марвел",
            youtubeurl: "https://www.youtube.com/embed/" + "gbcVZgO4n4E",
            description: "1995 год. Хала, столица Империи Кри. Верс, член элитного разведывательного отряда «Звёздная сила», страдает от постоянных ночных кошмаров. Йон-Рогг, её личный наставник и командор отряда, уже несколько лет обучает её контролировать свои способности и эмоции. А Высший Разум (искусственный интеллект, правительство Кри) призывает Верс верно служить своей расе",
        };

        this.android = platform() === "android";

    }

    componentDidMount() {
        document.body.className = " fixed";
        document.body.style.overflow = 'hidden';
        // document.body.style.animation="start  2s ease";
        window.addEventListener('load', function () {
                return;
                console.log("Check color");
                var
                    fac = new FastAverageColor(),
                    container = document.querySelector('.filmsearchcard'),
                    color = fac.getColor(container.querySelector('img'));

                container.style.backgroundColor = color.rgba;
                container.style.color = color.isDark ? '#fff' : '#000';

                console.log(color);
            }, false
        )
    }

    showTreiler = () => {
        this.setState({
            youtube: this.state.youtube !== true
        })
        console.log(this.state.youtube)
    };
    closeTreiler = () => {
        this.setState({
            youtube: false
        })
    };
    stopTouch = () => {
        console.log("STOP TPUCH");
        this.parent.setMove(false);
        var f = window.onmouseup;
        window.onmouseup = () => {
            console.log("START TPUCH");
            this.parent.setMove(true);
            window.onmouseup = f;
        }
    };
    stars = () => {
        var s = [];
        for (var i = 0; i < this.state.stars; i++) {
            s.push(<Icon24Favorite className={"star"}/>)
        }
        for (var i = this.state.stars; i < 10; i++) {
            s.push(<Icon24FavoriteOutline className={"star"}/>)
        }
        return s;
    };
    openURL = (url) => {
        window.open(url, '_blank');
    };
    openFilmCard = () => {
        this.parent.setFilm(this.state.film_id);
        document.body.className = "";
        document.body.style.overflow = 'auto';
    };

    render() {

        //upload our records

        return (
            <Card className={"filmsearchcard"} style={{"border-radius": "20px 20px 10px 10px"}}
                  onClick={this.props.onClick}>
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
                <div
                    color="secondary"
                    style={{
                        position: "absolute",
                        display: "inline-block"
                    }
                    }
                    className={"stars"}>
                    {this.stars()}
                </div>
                <div className={"content"}>
                    <img
                        className={"search_avatar"}
                        alt="Film Avatar"
                        src={this.state.avatar}
                    />
                    {this.state.youtube &&
                    <div style={{position: "absolute"}}
                              className={"card_youtube"}>
                        <iframe src={this.state.youtubeurl}
                                className={"frame_youtube"}
                                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen/>
                    </div>
                    }
                    <Div className={"filmtitle"} style={
                        {
                            display: 'flex',
                        }}>
                        <h2>{this.state.name}</h2>
                        <Button size="s" className={"openFilmCard"} stretched
                                onClick={this.openFilmCard}
                        > Подробнее</Button>
                    </Div>
                    <Div className={"filminfo"} onMouseDown={this.stopTouch}>
                        <p>{this.state.description}</p>
                    </Div>

                </div>

                <div className={"show_btn"} style={{position: "absolute"}}>
                    <Div style={
                        {
                            display: 'flex',
                        }}>
                        <Button size="l" stretched onClick={() => this.openURL(this.state.url1)}
                                className={"KinoPoisk"} style={{marginRight: 8}}>Кинопоиск</Button>

                        <Button size="l" stretched onClick={() => this.openURL(this.state.url2)}
                                className={"IVI"}> IVI</Button>
                    </Div>
                </div>
            </Card>
        )
    }
}








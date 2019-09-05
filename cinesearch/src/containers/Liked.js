import React from 'react';
import {
    CellButton,
    Div,
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
    View
} from '@vkontakte/vkui';
import "../css/Home.css"
import Film from "./Film";
import Icon24Back from '@vkontakte/icons/dist/24/back';
import FilmCardLong from "../components/FilmCardLong";


export default class Home extends React.Component {
    constructor(props) {
        super(props);
        // this.store = props.store;
        // this.dispatch = props.dispatch;

        this.state = {
            actPanel: "menu",//active panel
            id: props.id,//view id
            popuot: null,
            films:[
                {
                    film_id:12,
                    name:"Мстители",
                    about:"Лучший фильм всех времн и народов",
                    avatar:"https://st.kp.yandex.net/images/film_big/263531.jpg"
                },
                {
                    film_id:13,
                    name:"Мстители",
                    about:"Лучший фильм всех времн и народов",
                    avatar:"https://st.kp.yandex.net/images/film_big/263531.jpg"
                }
            ]
        };

        this.android = platform() == "android";

    }
    setFilm=(film_id)=>{
        console.log("Film");
        this.setState({
            actPanel: "film",
            film_id:film_id
        })

    };
    filmCards=()=>{
        var ar =[];
        var films = this.state.films;
        for(let f in films){
            ar.push(<FilmCardLong onClick={()=>this.setFilm(0)} main={this} {...films[f]}/>)
        }
        return ar
    };
    deleteFilm=(film_id)=>{
        var films = this.state.films;
        var ffilms = [];
        for(let f in films){
            if(films[f].film_id!==film_id)
                ffilms.push(films[f]);
        }
        this.setState({
            films:ffilms
        });

    };
    likeFilm=(film_id)=>{
        var films = this.state.films;
        var ffilms = [];
        for(let f in films){
            if(films[f].film_id!==film_id)
                ffilms.push(films[f]);
        }
        this.setState({
            films:ffilms
        });

    };


    render() {
        //upload our records

        return (
            <View id={this.state.id} popout={this.state.popout} activePanel={this.state.actPanel}>
                <Panel id="menu">
                    <PanelHeader>
                        Мои фильмы
                    </PanelHeader>
                    {
                        this.filmCards()
                    }

                </Panel>
                <Panel id={"film"}>
                    <PanelHeader left={<HeaderButton onClick={()=>this.setState({actPanel: "menu"})}><Icon24Back/></HeaderButton>}>
                        Мстители
                    </PanelHeader>
                    <Film  film_id={this.state.film_id}/>
                </Panel>

            </View>
        )
    }
}



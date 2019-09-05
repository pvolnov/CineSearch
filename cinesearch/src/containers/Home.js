import React from 'react';
import ReactDOM from 'react-dom';
import {
    Alert,
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
    HorizontalScroll,
    PanelHeaderContent,
    platform,
    ScreenSpinner,
    View
} from '@vkontakte/vkui';
import FilmBlock from "../components/FilmBlock";
import FilmCardMini from "../components/FilmCardMini";
import "../css/Home.css"
import Film from "./Film";
import Icon24Back from '@vkontakte/icons/dist/24/back';


export default class Home extends React.Component {
    constructor(props) {
        super(props);
        // this.store = props.store;
        // this.dispatch = props.dispatch;

        this.state = {
            actPanel: "menu",//active panel
            id: props.id,//view id
            popuot: null
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


    render() {
        //upload our records

        return (
            <View id={this.state.id} popout={this.state.popout} activePanel={this.state.actPanel}>
                <Panel id="menu">
                    <PanelHeader>
                        Главная
                    </PanelHeader>
                    <FilmBlock onClick={this.props.main.FilmSearch}/>
                    <Div/>
                    <Group title={"Новинки Кино"} className={"horisontalview"}>
                        <HorizontalScroll >
                            <div style={{display: 'flex'}} onClick={()=>this.setFilm(0)}>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                            </div>
                        </HorizontalScroll>
                    </Group>

                    <Group title={"Недавно вышло в цифре"} className={"horisontalview"}>
                        <HorizontalScroll >
                            <div style={{display: 'flex'}}>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                            </div>
                        </HorizontalScroll>
                    </Group>

                    <Group title={"Самые рейтинговые фильмы"} className={"horisontalview"}>
                        <HorizontalScroll >
                            <div style={{display: 'flex'}}>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                                <FilmCardMini name={"Мстители 4: Война бесконечности"}
                                              avatar={"https://st.kp.yandex.net/im/poster/3/2/1/kinopoisk.ru-The-Avengers-3214521.jpg"}/>
                            </div>
                        </HorizontalScroll>
                    </Group>

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



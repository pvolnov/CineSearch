import React from 'react';
import {
    Alert,
    Cell,
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
    Touch,
    View
} from '@vkontakte/vkui';
import "../css/CineSearch.css"
import Film from "./Film";
import Icon24Back from '@vkontakte/icons/dist/24/back';
import FilmSearchBlock from "../components/FilmSearchBlock";
import Icon24Home from '@vkontakte/icons/dist/24/home';
import {disableScroll, enableScroll} from "../function";

const circleStyle = {
    position: 'absolute',

    // left: '50%',
    // top: '50%'
};


export default class Home extends React.Component {

    constructor(props) {

        super(props);
        this.home = () => {
            props.main.setState({
                activeStory: "home"
            })
        };

        var f = [1,2,3,4,5,6];
        this.state = {
            allfilm:f,
            films: [ f[0] ],
            film_id: 1,
            shiftX: 0,
            shiftY: 0,
            actPanel: "menu",
            move: false,
            del: false,
            like: false,
            showed: false,
            deleted: false
        };

        this.startX = 0;
        this.startY = 0;
        this.moveacept = true;

        this.onMove = this.onMove.bind(this);
        this.onEnd = this.onEnd.bind(this);
        this.MoveStart = this.MoveStart.bind(this);
        this.getCircleRef = this.getCircleRef.bind(this);
    }

    componentWillUnmount() {
        document.body.className = "";
        document.body.style.overflow = 'auto';
    }

    componentDidMount() {
        document.body.className += " fixed";
        document.body.style.overflow = 'hidden';
        // document.body.style.animation=;

        this.limitY = window.screen.height;
        this.wight = this.circleRef.offsetWidth;
        this.hight = this.circleRef.offsetHeight;

        this.screenX = document.body.offsetWidth;
        this.screenY = document.body.offsetHeight;
    }
    setFilm=(film_id)=>{
        console.log("Film");
        this.setState({
            actPanel: "film",
            film_id:film_id
        })

    };
    setMove = (t) => {
        this.moveacept = t;

    };


    onMove(e) {
        if (!this.moveacept) {
            return;
        }

        let shiftX = this.startX + e.shiftX;
        let shiftY = this.startY + e.shiftY;

        let del= e.shiftX  <  -this.screenX / 8,
            like = !del && e.shiftX > this.screenX / 8,
            showed = !del && !like && e.shiftY < - this.screenX / 8

        this.setState({
            shiftX: shiftX,
            shiftY: Math.min(shiftY, this.limitY / 2 - 50),
            del: del,
            like: like,
            showed: showed
        }
        );
    }

    onEnd(e) {
        var main = this;

        if (this.state.showed || this.state.like || this.state.del) {
            setTimeout(() => {
                main.state.films.pop();
                main.state.allfilm.pop();
                main.state.films.push(main.state.allfilm[0]);
                main.setState({deleted: false})
            }, 1000);

            this.setState({deleted: true})
        }


        this.setState({
            shiftX: 0,
            shiftY: 0,
            del: false,
            like: false,
            move: false,
            showed: false
        });
        // allow page scroll
        enableScroll()
    }

    MoveStart(e) {
        this.setState({
            move: true
        });
        disableScroll();
    }

    getCircleRef(el) {
        this.circleRef = el
    };

    drowCards = () => {
        var main = this;
        let films = this.state.films;
        let ar = [];
        for (let f = films.length - 1; f >= 0; f--) {
            ar.push(
                <Touch
                    key={f}
                    getRootRef={this.getCircleRef}
                    onMove={this.onMove}
                    onEnd={this.onEnd}
                    onStart={this.MoveStart}
                    style={
                        {
                            transition: !this.state.move && "transform 0.2s",
                            ...circleStyle,
                            transform: (this.state.film_id === films[f]) && `translate(${this.state.shiftX}px, ${this.state.shiftY}px)`
                        }
                    }
                >
                    <div className={"FilmBox " +
                    (this.state.film_id === films[f] && this.state.move ? " MoveFilmBox " : "") +
                    (this.state.film_id === films[f] && this.state.del ? " FilmBoxDel" : "") +
                    (this.state.film_id === films[f] && this.state.like ? " FilmBoxLike" : "") +
                    (this.state.film_id === films[f] && this.state.showed ? " FilmBoxShowed" : "") +
                    (this.state.film_id === films[f] && this.state.deleted ? " FilmBoxDeleted" : "")
                    }>
                        <FilmSearchBlock main={this} film_id={films[f]}/>

                    </div>
                </Touch>)
        }
        return ar;
    };


    render() {
        const {shiftX, shiftY} = this.state;

        return (
            <View id={this.state.id} popout={this.state.popout} activePanel={this.state.actPanel}>
                <Panel id="menu" >
                    <PanelHeader left={<HeaderButton onClick={this.home}>
                        <Icon24Home/></HeaderButton>}>
                        <span className={"header"}>Cine Search</span>
                    </PanelHeader>

                    {this.drowCards()}

                </Panel>


                <Panel id={"film"}>
                    <PanelHeader left={<HeaderButton
                        onClick={() => this.setState({actPanel: "menu"})}><Icon24Back/></HeaderButton>}>
                        Мстители
                    </PanelHeader>
                    <Film film_id={this.state.film_id}/>
                </Panel>

            </View>
        )
    }
}



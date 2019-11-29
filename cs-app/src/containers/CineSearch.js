import React from 'react';
import {HeaderButton, Panel, PanelHeader, View} from '@vkontakte/vkui';
import Icon24Home from '@vkontakte/icons/dist/24/home';


export default class CineSearch extends React.Component {

    constructor(props) {

        super(props);
        this.state = {
            films: [1],
            actPanel:"menu"
        };

    }

    home = ()=>{

    };


    render() {

        return (
            <View id={this.state.id} popout={this.state.popout} activePanel={this.state.actPanel}>
                <Panel id="menu" >
                    <PanelHeader left={<HeaderButton onClick={this.home}>
                        <Icon24Home/></HeaderButton>}>
                        <span className={"header"}>Cine Search</span>
                    </PanelHeader>

                </Panel>
            </View>
        )
    }
}



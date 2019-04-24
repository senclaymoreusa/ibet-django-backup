// Navigation components test

import React from 'react';
import { Navigation } from '../navigation';
import { NavLink } from 'react-router-dom';


describe('Navigation Component', () => {

    const wrapper = shallow(<Navigation lang ={'en'}/>);

    //Testing User Interactive Event
    it('should call redirect to / page', () => {
        expect(wrapper.find(NavLink).first().props().to).toEqual('/');
    });

    it('should call redirect to game type page', () => {
        expect(wrapper.find(NavLink).at(1).props().to).toEqual('/game_type/');
    });

});
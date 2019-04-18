import React from 'react';
import { shallow } from 'enzyme';
import { Home } from '../home';

const setUp = (props={}) => {
    const component = shallow(<Home {...props} />);
    return component;
};

const findByTestAtrr = (component, attr) => {
    const wrapper = component.find(`[data-test='${attr}']`);
    return wrapper;
};

describe('Home Component', () => {

    let component;
    beforeEach(() => {
        component = setUp();
    });
    
    //Snapshot test
    it('should render without throwing an error', () => {
        expect(component).toMatchSnapshot();
    });

    //Components test
    it('should have one header', () => {
        const wrapper = findByTestAtrr(component, 'headerLine');
        expect(wrapper.length).toBe(1);
    });

    it('should render a H1', () => {
        const h1 = findByTestAtrr(component, 'header');
        expect(h1.length).toBe(1);
    });


});
 
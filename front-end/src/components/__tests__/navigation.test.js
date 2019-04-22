import { Navigation } from '../navigation';
import { NavLink } from 'react-router-dom';



describe('Navigation Component', () => {

    //Testing User Interactive Event
    it('should call mock function when button is clicked', () => {
        const wrapper = shallow(<Navigation lang ={'en'}/>);
        expect(wrapper.find(NavLink).first().props().to).toEqual('/');
    });

});
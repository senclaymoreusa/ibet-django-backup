import React, { Component } from 'react';
import axios from 'axios';
import { NavLink, withRouter } from 'react-router-dom';

const API_URL = process.env.REACT_APP_REST_API

class Update extends Component {

    constructor(props){
        super(props);

        this.state = {
            username: '',
            email: '',
            first_name: '',
            last_name: '',
            phone: '',
            date_of_birth: '',
            street_address_1: '',
            street_address_2: '',
            country: '',
            city: '',
            zipcode: '',
            state: '',
            
            fetched_data: {}
        }

        this.onInputChange_username         = this.onInputChange_username.bind(this);
        this.onInputChange_email            = this.onInputChange_email.bind(this);
        this.onInputChange_first_name       = this.onInputChange_first_name.bind(this);
        this.onInputChange_last_name        = this.onInputChange_last_name.bind(this);
        this.onInputChange_phone            = this.onInputChange_phone.bind(this);
        this.onInputChange_date_of_birth    = this.onInputChange_date_of_birth.bind(this);
        this.onInputChange_street_address_1 = this.onInputChange_street_address_1.bind(this);
        this.onInputChange_street_address_2 = this.onInputChange_street_address_2.bind(this);
        this.onInputChange_country          = this.onInputChange_country.bind(this);
        this.onInputChange_city             = this.onInputChange_city.bind(this);
        this.onInputChange_zipcode          = this.onInputChange_zipcode.bind(this);
        this.onInputChange_state            = this.onInputChange_state.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }
    
    async componentDidMount() {
      const token = localStorage.getItem('token');
      const config = {
        headers: {
          "Content-Type": "application/json"
        }
      };
      config.headers["Authorization"] = `Token ${token}`;

      await axios.get(API_URL + 'users/api/user/', config)
        .then(res => {
            this.setState({fetched_data: res.data})
        })

      this.setState({
          username:         this.state.fetched_data.username,
          email:            this.state.fetched_data.email,
          first_name:       this.state.fetched_data.first_name,
          last_name:        this.state.fetched_data.last_name,
          phone:            this.state.fetched_data.phone,
          date_of_birth:    this.state.fetched_data.date_of_birth,
          street_address_1: this.state.fetched_data.street_address_1,
          street_address_2: this.state.fetched_data.street_address_2,
          country:          this.state.fetched_data.country,
          city:             this.state.fetched_data.city,
          zipcode:          this.state.fetched_data.zipcode,
          state:            this.state.fetched_data.state
    })
    }

    onInputChange_username(event){
        this.setState({username: event.target.value});
    }

    onInputChange_email(event){
        this.setState({email: event.target.value});
    }

    onInputChange_first_name(event){
        this.setState({first_name: event.target.value});
    }

    onInputChange_last_name(event){
        this.setState({last_name: event.target.value});
    }

    onInputChange_phone(event){
        this.setState({phone: event.target.value});
    }

    onInputChange_date_of_birth(event){
        this.setState({date_of_birth: event.target.value});
    }

    onInputChange_street_address_1(event){
        this.setState({street_address_1: event.target.value});
    }

    onInputChange_street_address_2(event){
        this.setState({street_address_2: event.target.value});
    }

    onInputChange_country(event){
        this.setState({country: event.target.value});
    }

    onInputChange_city(event){
        this.setState({city: event.target.value});
    }

    onInputChange_zipcode(event){
        this.setState({zipcode: event.target.value});
    }

    onInputChange_state(event){
        this.setState({state: event.target.value});
    }

    onFormSubmit(event){
        event.preventDefault();

        const token = localStorage.getItem('token');
        const config = {
        headers: {
          "Content-Type": "application/json"
          }
        };
        config.headers["Authorization"] = `Token ${token}`;

        const body = JSON.stringify({ 
            username:         this.state.username         ? this.state.username         : this.state.fetched_data.username, 
            email:            this.state.email            ? this.state.email            : this.state.fetched_data.email, 
            first_name:       this.state.first_name       ? this.state.first_name       : this.state.fetched_data.first_name, 
            last_name:        this.state.last_name        ? this.state.last_name        : this.state.fetched_data.last_name,
            phone:            this.state.phone            ? this.state.phone            : this.state.fetched_data.phone, 
            date_of_birth:    this.state.date_of_birth    ? this.state.date_of_birth    : this.state.fetched_data.date_of_birth,
            street_address_1: this.state.street_address_1 ? this.state.street_address_1 : this.state.fetched_data.street_address_1,
            street_address_2: this.state.street_address_2 ? this.state.street_address_2 : this.state.fetched_data.street_address_2,
            country:          this.state.country          ? this.state.country          : this.state.fetched_data.country,
            city:             this.state.city             ? this.state.city             : this.state.fetched_data.city,
            state:            this.state.state            ? this.state.state            : this.state.fetched_data.state,
            zipcode:          this.state.zipcode          ? this.state.zipcode          : this.state.fetched_data.zipcode
      });
      if (!this.state.email){
          alert('Email cannot be empty')
      }else if (!this.state.first_name){
          alert('First name cannot be empty')
      }else if (!this.state.last_name){
          alert('Last name cannot be empty')
      }else if (!this.state.phone){
          alert('Phone cannot be empty')
      }else if (!this.state.date_of_birth){
          alert('Date of Birth cannot be empty')
      }else if(!this.state.country){
          alert('Country cannoe be empty')
      }else if (!this.state.zipcode){
          alert('Zipcode cannot be empty')
      }else if(!this.state.state){
          alert('State cannot be empty')
      }else if(!this.state.street_address_1){
          alert("Street Address 1 cannot be empty")
      }else if(!this.state.street_address_2){
          alert("Street Address 2 cannot be empty")
      }else{
        axios.put(API_URL + 'users/api/user/', body, config)
        this.props.history.push("/profile")
      }
    }

    render() {
        return (
            <div> 
                <form onSubmit={this.onFormSubmit} >

                    <div>
                        <div><b>Username</b>: {this.state.username} </div>
                    </div>

                    <div>
                        <b>Email</b>: {this.state.email}
                        <button> 
                            <NavLink to='/change_email/' style={{ textDecoration: 'none' }}>
                                Update Email
                            </NavLink>
                        </button>
                    </div>

                    <div>
                        <label><b>First Name:</b></label>
                        <input
                            placeholder="Mike"
                            className="form-control"
                            value={this.state.first_name}
                            onChange={this.onInputChange_first_name}
                        />
                    </div>

                    <div>
                        <label><b>Last Name:</b></label>
                        <input
                            placeholder="Shaw"
                            className="form-control"
                            value={this.state.last_name}
                            onChange={this.onInputChange_last_name}
                        />
                    </div>

                    <div>
                        <label><b>Phone:</b></label>
                        <input
                            placeholder="123456789"
                            className="form-control"
                            value={this.state.phone}
                            onChange={this.onInputChange_phone}
                        />
                    </div>

                    <div>
                        <label><b>Date of Birth:</b></label>
                        <input
                            placeholder="mm/dd/yyyy"
                            className="form-control"
                            value={this.state.date_of_birth}
                            onChange={this.onInputChange_date_of_birth}
                        />
                    </div>

                    <div>
                        <label><b>Street Address 1:</b></label>
                        <input
                            placeholder="111 World Drive"
                            className="form-control"
                            value={this.state.street_address_1}
                            onChange={this.onInputChange_street_address_1}
                        />
                    </div>

                    <div>
                        <label><b>Street Address 2:</b></label>
                        <input
                            placeholder="Suite No.123"
                            className="form-control"
                            value={this.state.street_address_2}
                            onChange={this.onInputChange_street_address_2}
                        />
                    </div>

                    <div>
                        <label><b>Country:</b></label>
                        <input
                            placeholder="United States"
                            className="form-control"
                            value={this.state.country}
                            onChange={this.onInputChange_country}
                        />
                    </div>

                    <div>
                        <label><b>City:</b></label>
                        <input
                            placeholder="Mountain View"
                            className="form-control"
                            value={this.state.city}
                            onChange={this.onInputChange_city}
                        />
                    </div>

                    <div>
                        <label><b>Zipcode:</b></label>
                        <input
                            placeholder="96173"
                            className="form-control"
                            value={this.state.zipcode}
                            onChange={this.onInputChange_zipcode}
                        />
                    </div>

                    <div>
                        <label><b>State:</b></label>
                        <input
                            placeholder="CA"
                            className="form-control"
                            value={this.state.state}
                            onChange={this.onInputChange_state}
                        />
                    </div>
                    
                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
                            Submit 
                        </button>
                    </span>
                </form>
                <button style={{color: 'red'}} onClick={()=>{this.props.history.push("/profile")}}> 
                    Cancel 
                </button>
            </div>
        )
    }
}

export default withRouter(Update);
import React from 'react';
import MyInput from "../UI/input/MyInput";
import MySelect from "../UI/select/MySelect";

const EventFilter = ({filter, setFilter}) => {
    return (
        <div>
            <MyInput
                value={filter.query}
                onChange={e => setFilter({...filter, query:e.target.value})}
                placeholder="Search"
            />
            <MySelect
                value={filter.sort}
                onChange={selectedSort => setFilter({...filter, sort: selectedSort})}
                defaultValue="Sort by"
                options={[
                    {value: 'title', name: 'By title'},
                    {value: 'start_time', name: 'By date'}
                ]}
            />
        </div>
    );
};

export default EventFilter;
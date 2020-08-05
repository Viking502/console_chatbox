//
// Created by viking on 01.07.20.
//
#include <iostream>
#include <boost/asio.hpp>
#include <boost/array.hpp>

using boost::asio::ip::tcp;

int main(int argc, char* argv[]){

    if(argc != 3){
        std::cerr << "no host address or port given\n";
        return 1;
    }
    boost::asio::io_context io_context;
    tcp::resolver resolver(io_context);

    auto endpoints = resolver.resolve(argv[1], argv[2]);

    tcp::socket socket(io_context);
    boost::asio::connect(socket, endpoints);

    auto write_flag = true;
    while(write_flag){
        std::vector<char> buff(128);
        boost::system::error_code err;

        socket.read_some(boost::asio::buffer(buff), err);

        if(err == boost::asio::error::eof){
            write_flag = false;
        }else if(err){
            throw boost::system::system_error(err);
        }

        std::cout << buff.data() << "\n";
    }

    return 0;
}
//
// Created by viking on 01.07.20.
//

//#define DEBUG_FLAG

#include <exception>
#include <iostream>
#include <ctime>
#include <boost/asio.hpp>

using boost::asio::ip::tcp;

std::string get_timestamp(){
    std::time_t curr_time = std::time(nullptr);
    return ctime(&curr_time);
}

std::string get_message(const std::string& author, const std::string& message){
    return get_timestamp() + author + ": " + "\n" + message;
}

int main(int argc, char* argv[]){

    if(argc != 2){
        std::cerr << "no port given";
    }

    try{
        boost::asio::io_context io_context;
        tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), std::stoi(argv[1])));

        while(true){
            tcp::socket socket(io_context);
            acceptor.accept(socket);

            std::string msg = get_message("Server", "Hello!");

            boost::system::error_code ignored_err;
            boost::asio::write(socket, boost::asio::buffer(msg), ignored_err);
        }

    }catch (std::exception& ex){
        std::cerr << ex.what() << "\n";
    }

    return 0;
}
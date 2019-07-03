#include <iostream>
#include <mysql.h>
#include <cstdio>
#include <time.h>
#include <pthread.h>

using namespace std;

struct User {
    int id;
    string name;

    User(){}

    User(int id, string name) : id(id), name(name) {}
};

class Chatbox {

private:
    MYSQL* mysql;
    User user;

    string getCurDate() {
        time_t clock;
        time(&clock);
        struct tm *t = localtime(&clock);

        char c_date[20];
        sprintf(c_date, "%d-%02d-%02d %02d:%02d:%02d", t->tm_year + 1900, t->tm_mon + 1, t->tm_mday, t->tm_hour,
                t->tm_min, t->tm_sec);

        return c_date;
    }

public:
    Chatbox() {

    }

    ~Chatbox(){
        mysql_close(mysql); // disconnect
    }

    void displayMessages() {

        MYSQL_ROW row;
        MYSQL_RES *Id_query;

        mysql_query(mysql, "SELECT nick, message, date FROM posts");
        Id_query = mysql_store_result(mysql);

        string load_bufor;
        //wczytywanie postów
        while ((row = mysql_fetch_row(Id_query)) != nullptr) {
            load_bufor = (string) row[0] + "            ";
            load_bufor.insert(12, row[2]);
            cout << load_bufor << endl;
            cout << row[1] << "\n\n________________________________\n";
        }
    }

    bool sendMessage() {

        string message = "";
        string upp_query;

        cout << "________________________________\n" << user.name << endl;
        cout << "message: ";
        cin.ignore();
        getline(cin, message);

        if (message == "/exit") {
            mysql_close(mysql); // disconnect
            return 0;
        }

        if (message != "") {

            string date = getCurDate();

            upp_query = "INSERT INTO posts (`nick`, `message`, `date`) VALUES (\""+user.name + "\",\"" + message + "\",\"" + date + "\")";

            if (mysql_query(mysql, upp_query.c_str()) != 0) {
                mysql_close(mysql); // disconnect
                cout << "error!";
                getchar();
                return 0;
            }
        }
    }

    //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    /*
    void start(){
        pthread_t displayer_t;
        pthread_t sender_t;

        pthread_create(&displayer_t, NULL, display , (void*)&mysql );
    }
    */

    bool connectDatabase() {
        mysql_init(mysql); // incjalizacja

        if (mysql_real_connect(mysql, "127.0.0.1", "root", "asdqwe", "chatbox", 0, NULL, 0)) {
            printf("connected\n################################\n");
        } else {
            printf("Conecting with database failed: %d, %s\n", mysql_errno(mysql), mysql_error(mysql));
            return 0;
        }
        mysql_select_db(mysql, "chatbox");
        return 1;
    }

    User logginIn() {

        MYSQL_ROW row;
        MYSQL_RES *Id_query;
        bool logFlag = false;
        string nick = "", password = "";

        do {
            cout << "nick: ";
            cin >> nick;

            cout << "password: ";
            cin >> password;

            string que = "SELECT id FROM users WHERE nick = '" + nick + "' AND password = '" + password + "'";

            mysql_query(mysql, que.c_str());
            Id_query = mysql_store_result(mysql);

            if ((row = mysql_fetch_row(Id_query)) != NULL) {
                logFlag = true;
            }else{
                cout<<"wrond login or password\n";
            }
        } while (!logFlag);

        string id_s = (string) row[0];
        int id;

        sscanf(((string) row[0]).c_str(), "%d", &id);
        //cout<<"===\nid: "<<id<<"\n===\n";

        User user(id, nick);
        cout << "logged successfully\n";

        this->user = user;

        return user;
    }
};

int main(){

    Chatbox app;
    if(!app.connectDatabase()){
        cout<<"error!";
        //return 1;
    }else {
        app.logginIn();
    }


    while(true){

        app.displayMessages();

        if(!app.sendMessage()){
            return 0;
        }
    }


    return 0;
}

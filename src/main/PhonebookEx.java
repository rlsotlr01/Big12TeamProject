package main;

import java.util.Scanner;

import lib.Phonebook;

/**
 * @작성자 : 김동윤
 * @작성일 : 2020. 12. 22.
 * @filename : PhonebookEx.java
 * @package : main
 * @description : 전화번호부 프로그램 실행파일입니다.
 */
public class PhonebookEx {

     public static void main(String[] args) {
           Phonebook pb = new Phonebook();
           Scanner scanner = new Scanner(System.in);
           while(true) {
                          pb.printMenu();
                          String choice = scanner.nextLine();
                          if(choice.matches("1")) {
                                pb.addPhoneNumber(scanner);                   
                          }else if(choice.matches("2")) {
                                pb.showList();                    
                          }else if(choice.matches("3")) {
                                pb.editPerson(scanner);
                          }else if(choice.matches("4")) {
                                pb.removePerson(scanner);
                                
                          }else if(choice.matches("5")) {
                                System.out.println("프로그램이 종료됩니다.");
                                break;
                          }else {
                                System.out.println("1~5 사이의 숫자를 입력해주세요.");
                          }
                     
                     
           }
                scanner.close();
           }
     }


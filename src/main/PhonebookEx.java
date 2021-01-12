package main;

import java.util.Scanner;

import lib.Phonebook;

/**
 * @�ۼ��� : �赿��
 * @�ۼ��� : 2020. 12. 22.
 * @filename : PhonebookEx.java
 * @package : main
 * @description : ��ȭ��ȣ�� ���α׷� ���������Դϴ�.
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
                                System.out.println("���α׷��� ����˴ϴ�.");
                                break;
                          }else {
                                System.out.println("1~5 ������ ���ڸ� �Է����ּ���.");
                          }
                     
                     
           }
                scanner.close();
           }
     }


using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using System.Text.RegularExpressions;

namespace WindowsFormsApplication7
{
    public partial class Form1 : Form
    {
        Socket client;

        public Form1()
        {
            
            InitializeComponent();
            Clean();
            ThreadStart tstart=new ThreadStart(Thread_Function);
            Thread tserver = new Thread(tstart);
            tserver.IsBackground = true;
            tserver.Start();
        }
        private void Thread_Function()
        {

            Socket s = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
            IPAddress IP = IPAddress.Parse("127.0.0.1");
            IPEndPoint address = new IPEndPoint(IP, 1234);
            s.Bind(address);
            s.Listen(1);
            client = s.Accept();

            while (true)
                ClientList();
        }
        private void ClientList()
        {
            string Recieved_Massage = Recieve_Function();

            if (Recieved_Massage.Contains("disconnected"))
            {
                string[] arr = Recieved_Massage.Split('$');
                string[] arr2 = arr[1].Split('#');
                string IP = arr2[0];
                string Port = arr2[1];
                foreach (ListViewItem item in listView1.Items)
                {
                    if (item.SubItems[1].Text == IP && item.SubItems[2].Text == Port)
                        listView1.Items.Remove(item);
                }
            }
            else if (Recieved_Massage.Contains("Connected"))
            {
                string[] arr = Recieved_Massage.Split('#');
                string IP = arr[1];
                string Port = arr[2];
                ListViewItem item = new ListViewItem("1");
                item.SubItems.Add(IP);
                item.SubItems.Add(Port);
                listView1.Items.Add(item);
            }
            else if (Recieved_Massage.Contains("image_sent"))
                View_Image(Recieved_Massage);
            else
                Print_Exceptions(Recieved_Massage);
            
        }
        private string Recieve_Function()
        {
            byte[] byteBuffer = new byte[1024];
            int iLength = client.Receive(byteBuffer);
            return Encoding.UTF8.GetString(byteBuffer).Substring(0, iLength);

        }
        private void Send_Function(string message)
        {
            byte[] byteBuffer = Encoding.UTF8.GetBytes(message);
            int iLength = client.Send(byteBuffer);
            
        }

        private bool Check_Selected_Line()
        {
            if (listView1.SelectedItems.Count > 0)
                return true;
            else return false;
            
        }
        private void Check_Exceptions()
        {
            string process_name="";
            string a = "";

            string IP=listView1.SelectedItems[0].SubItems[1].Text;
            string port = listView1.SelectedItems[0].SubItems[2].Text;

            Dictionary<string, bool> exceptions = new Dictionary<string, bool>()
            {
                {"wmp",false},{"youtube",false},{"cpu",false},{"process",false}
            };

            if (checkBox1.Checked == true)
                exceptions["wmp"] = true;
            if (checkBox2.Checked == true)
                exceptions["youtube"] = true;
            if (checkBox3.Checked == true)
                exceptions["cpu"] = true;
            if (checkBox4.Checked == true)
            {
                exceptions["process"] = true;
                process_name = textBox1.Text;
            }
            foreach (KeyValuePair<string, bool> kvp in exceptions)
            {
                a += kvp.Value.ToString()+"#";
                if (kvp.Key == "process"&&kvp.Value==true)
                    a += process_name;
            }
            string message = IP + "$" + port+"$"+a+"$"+textBox2.Text;
            Send_Function(message);
        }

        private void Print_Exceptions(string Recieved_Massage)
        {
            
            label4.Text = "Check finished ! ";
            int ExcCounter = 0;
            progressBar1.Maximum=int.Parse(textBox2.Text);
            string[] arr = Recieved_Massage.Split('$');
            string[] arr1;
            for (int i = 0; i < arr.Length-1; i++)
            {
                arr1= arr[i].Split('_');
                if (arr[i].Contains("wmp"))
                {
                    if (arr[i].Contains("True"))
                    {
                        ExcCounter++;
                        WMP_Label.Text += ("Windows Media Player");
                    }
                    else
                        WMP_Label.Text += ("User doesn't use Windows Media Player");
                }
                if (arr[i].Contains("youtube"))
                {
                    if (arr[i].Contains("True"))
                    {
                        ExcCounter++;
                        YouTube_Label.Text += ("YouTube");
                    }
                    else
                        YouTube_Label.Text += ("User doesn't use youtube");
                }
                if (arr[i].Contains("cpu"))
                {
                    if (arr[i].Contains("True"))
                    {
                        ExcCounter++;
                        CPU_Label.Text += ("CPU");
                    }
                    else
                        CPU_Label.Text += ("There is not an exception in the CPU");
                }
                if (arr[i].Contains("process"))
                {
                    if (arr[i].Contains("True"))
                    {
                        ExcCounter++;
                        Process_Label.Text += (textBox1.Text);
                    }
                    else
                        Process_Label.Text += ("User doesn't use  " + textBox1.Text);
                }

            }
            Exception_Label.Text += ("\r\n" + "There is " + ExcCounter + " exceptions from " + (arr.Length - 1) + "\r\n" + "\r\n" + "Enter process name and " + "\r\n" + "press the Print Screen button");
        }
        private void View_Image(string  message)
        {   
            
            string[] arr = message.Split('#');
            string Path = arr[1];
            pictureBox1.Image = new Bitmap(Path);
            pictureBox1.SizeMode = PictureBoxSizeMode.Zoom;
        }
        private RichTextBox str(bool p)
        {
            throw new NotImplementedException();
        }
        private void listView1_SelectedIndexChanged(object sender, EventArgs e)
        {
            
        }

        private void Form1_Load(object sender, EventArgs e)
        {

        }

        private void groupBox1_Enter(object sender, EventArgs e)
        {

        }

        private void groupBox2_Enter(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void progressBar1_Click(object sender, EventArgs e)
        {
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (!Check_Selected_Line())
                System_Label.Text += "You must select client from the list\r\n";
            else
            {
                progressBar1.ForeColor = Color.Black;
                label4.Text = "Checking exceptions...";
                int time = Int32.Parse(textBox2.Text);
                Regex x = new Regex(@"^(0-9)*$");
                x.IsMatch(////////////////////////////////////////////////////////////////////////////////////
                if (time>0&&
                time = time * 600;
                timer1.Interval = time;
                this.timer1.Start();

                ThreadStart tstart = new ThreadStart(Check_Exceptions);
                Thread tserver = new Thread(tstart);
                tserver.IsBackground = true;
                tserver.Start();
            }

        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {

        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            this.progressBar1.Increment(1);
        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void groupBox3_Enter(object sender, EventArgs e)
        {

        }

        private void richTextBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void button2_Click(object sender, EventArgs e)
        {
           System_Label.Text+="This is not legal";
           Send_Function(textBox3.Text);              
        }

        private void label6_Click(object sender, EventArgs e)
        {

        }

        private void pictureBox1_Click(object sender, EventArgs e)
        {
        
        }

        private void button3_Click(object sender, EventArgs e)
        {
            Clean();
        }
        private void Clean()
        {
            Exception_Label.Text = "";
            WMP_Label.Text = "";
            YouTube_Label.Text = "";
            CPU_Label.Text = "";
            Process_Label.Text = "";
            label4.Text = "";
            System_Label.Text = "";
            checkBox1.Checked = false;
            checkBox2.Checked = false;
            checkBox3.Checked = false;
            checkBox4.Checked = false;
        }
        private void label7_Click(object sender, EventArgs e)
        {

        }

        private void pictureBox2_Click(object sender, EventArgs e)
        {

        }
    }
}
